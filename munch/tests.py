from django.test import TestCase, Client
from .models import Author, Entry, Comment, Like, Follow
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from django.urls import reverse
from unittest.mock import patch
from munch.utils import sync_github_activity
from rest_framework.test import APIClient
import unittest

# Create your tests here.

############################
# IDENTITY USER STORY TEST #
###########################
# The following test class from Google, Gemini, "Django Author Identity tests", 03-01-2026
class AuthorTest(TestCase):
    def setUp(self):
        # Setup basic data for testing
        self.client = Client()
        self.author_data = {
            'username': 'joshua1',
            'password': 'password123',
            'displayName': 'Joshua 1',
            'github': 'https://github.com/joshua',
            'description': 'Hello world'
        }
        self.author = Author.objects.create_user(**self.author_data)
        # Setup a second user to act as a visitor/friend
        self.visitor = Author.objects.create_user(
            username='visitor1', 
            password='password123', 
            displayName='Visitor'
        )

    ## STORY: Consistent Identity per Node
    def test_identity_consistency_and_predictability(self):
        """
        Tests that FQID (id) and Web URLs are generated correctly and stay predictable.
        """
        # Check API FQID (id)
        self.assertTrue(self.author.id.endswith(f"authors/{self.author.uuid}"))
        self.assertIn("/munch/api/", self.author.id)
        
        # Check Web URL (web)
        self.assertIn("/munch/authors/", self.author.web)
        self.assertNotIn("api/", self.author.web)
        
        # Ensure they don't change on second save
        old_id = self.author.id
        self.author.displayName = "New Name"
        self.author.save()
        self.assertEqual(self.author.id, old_id)

    ## STORY: Host Multiple Authors
    def test_host_multiple_authors(self):
        """
        Verify the node can handle multiple unique identities.
        """
        initial_count = Author.objects.count()
        
        # Create a new unique author
        author2 = Author.objects.create_user(username="joshua2", displayName="Joshua 2")
        
        # Verify uniqueness
        self.assertNotEqual(self.author.uuid, author2.uuid)
        self.assertNotEqual(self.author.id, author2.id)
        
        # Check that exactly one new author was added
        self.assertEqual(Author.objects.count(), initial_count + 1)

    ## STORY: Public Profile Page
    def test_public_profile_page_resolves(self):
        """
        Tests that the web frontend profile page is accessible.
        """
        url = reverse('munch:public_profile', kwargs={'author_uuid': self.author.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.author.displayName)
        self.assertContains(response, self.author.id) # Show FQID on page

    def test_profile_entry_visibility_logic(self):
        """
        Tests that entries show up on the profile correctly based on visibility.
        - Stranger sees Public
        - Friend sees Private
        - No one sees Deleted
        """
        # Create test entries
        Entry.objects.create(author=self.author, title="Public Post", visibility='PUBLIC')
        Entry.objects.create(author=self.author, title="Private Post", visibility='PRIVATE')
        Entry.objects.create(author=self.author, title="Deleted Post", visibility='DELETED')

        url = reverse('munch:public_profile', kwargs={'author_uuid': self.author.uuid})

        # 1. Test as Stranger (Logged in but no follow relationship)
        self.client.login(username='visitor1', password='password123')
        response = self.client.get(url)
        self.assertContains(response, "Public Post")
        self.assertNotContains(response, "Private Post")
        self.assertNotContains(response, "Deleted Post")

        # 2. Test as Friend (Mutual Follow)
        Follow.objects.create(actor=self.visitor, object=self.author, status='accepted')
        Follow.objects.create(actor=self.author, object=self.visitor, status='accepted')
        
        response = self.client.get(url)
        self.assertContains(response, "Public Post")
        self.assertContains(response, "Private Post")
        self.assertNotContains(response, "Deleted Post")

    ## STORY: Edit Profile (UI/Browser)
    def test_edit_profile_via_browser(self):
        """
        Tests the user story: Manage profile via web browser.
        """
        self.client.login(username='joshua1', password='password123')
        update_data = {
            'displayName': 'Joshua Updated',
            'description': 'Updated bio',
            'github': 'https://github.com/joshua-new',
            'profileImage': 'https://example.com/pic.jpg'
        }
        url = reverse('munch:edit_profile')
        response = self.client.post(url, update_data)
        
        # Should redirect back to profile on success
        self.author.refresh_from_db()
        self.assertEqual(self.author.displayName, 'Joshua Updated')
        self.assertEqual(self.author.github, 'https://github.com/joshua-new')

# The following test function from Google, Gemini, "Django Author Identity tests", 03-11-2026
    ## STORY: Edit Profile (API)
    def test_edit_profile_via_api(self):
        """
        Tests the user story: Manage profile via REST API.
        """
        # Initialize the API Client
        api_client = APIClient()
        
        # Authenticate as the author
        api_client.force_authenticate(user=self.author)
        
        # Define the API URL
        # Based on your view logic, this uses the author's UUID
        url = reverse('munch:get_author', kwargs={'author_id': self.author.uuid})
        
        update_json = {
            'displayName': 'API Joshua',
            'description': 'Bio updated via API',
            'github': 'https://github.com/api-joshua',
            'profileImage': 'https://example.com/api-pic.jpg'
        }
        
        # Send PUT request with JSON data
        response = api_client.put(url, update_json, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        
        self.author.refresh_from_db()
        self.assertEqual(self.author.displayName, 'API Joshua')
        self.assertEqual(self.author.description, 'Bio updated via API')
        self.assertEqual(self.author.github, 'https://github.com/api-joshua')
        
        # Verify that read-only fields like 'id' did not change
        old_id = self.author.id
        self.assertEqual(response.data['id'], old_id)


# The following test class from Google, Gemini, "Django Github Activity tests", 03-11-2026
class GitHubTest(TestCase):
    @patch('requests.get') # Intercept the requests.get call
    def test_github_sync_creates_entry(self, mock_get):
        # 1. Define what the 'fake' GitHub API should return
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            'id': '12345',
            'type': 'PushEvent',
            'repo': {'name': 'test-repo'},
            'created_at': '2026-03-01T12:00:00Z'
        }]

        # 2. Run your sync function
        author = Author.objects.create(username="test", github="https://github.com/test")
        sync_github_activity(author)

        # 3. Assert that a local entry was actually created
        self.assertEqual(Entry.objects.filter(github_id='12345').count(), 1)

###########################
# POSTING USER STORY TEST #
##########################

class PostingTest(TestCase):
  def setUp(self):
    self.client = Client()
    self.user = Author.objects.create_user(
      username = 'posty',
      password='ilove6767',
      displayName = 'posty the post tester!',
      is_approved = True,
    )
    self.client.login(username='posty', password='ilove6767')

  def mockEntry(self):
    entry = Entry.objects.create(
      author = self.user,
      title='testing',
      content='this is test for PostingTest',
      contentType="text/plain",
      visibility='PUBLIC',
      description='this is a test under StreamAPITest',
    )

    return entry

  # Tests creating an entry by checking if we can access the entry's details page
  def test_create_entry(self):
    #lets first create an entry 
    entry = self.mockEntry()
    response = self.client.get(f"/munch/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)

  # Tests modifying an entry by checking if the content changed before and after modification
  def test_edit_entry(self):
    entry = self.mockEntry()
    initial_content = entry.content
    response = self.client.get(f"/munch/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    self.client.post(
      f"/munch/authors/{self.user.uuid}/entries/{entry.serial}/edit/",
      {
        "author": self.user,
        "title": 'Posty posts',
        "content":'post messages in here',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    entry.refresh_from_db()
    post_content = entry.content
    self.assertNotEqual(initial_content,post_content)
    
  # Tests deleting an entry by checking if the visibility of the entry is 'DELETED' after deletion
  def test_delete_entry(self):
    entry = self.mockEntry()
    response = self.client.get(f"/munch/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    self.client.post(f'/munch/authors/{self.user.uuid}/entries/{entry.serial}/delete/')
    entry.refresh_from_db()
    self.assertEqual(entry.visibility,"DELETED")

class ImageEntryAPITest(TestCase):
  
  def setUp(self):
    self.client = APIClient()
    self.author = Author.objects.create_user(
        username='catmemesonly',
        password='meowUWUniao8',
        displayName='Cat Meme Enjoyer',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    self.friend = Author.objects.create_user(
        username='NemoTheFish',
        password='findingthingslol',
        displayName='Nemo',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    self.stranger = Author.objects.create_user(
        username='StrangerShrek',
        password='donkeykongRAAH999',
        displayName='Shrek 2 is out now on DVD!',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')
    
    # Source: https://stackoverflow.com/questions/37785233/how-to-create-the-smallest-possible-transparent-png-gif-of-a-given-size-in-php
    #used the string in the comments and also validated it using
    #python3 -c "import base64; data = 'iVBORw0KGgoAAAANSUhEUgAAA/gAAAE4AQMAAADVYspJAAAAA1BMVEUEAgSVKDOdAAAAPUlEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/BicAAABWZX81AAAAABJRU5ErkJggg=='; base64.b64decode(data); print('valid!')"
    # Date Accessed: Sunday, March 15, 2026
    # 1x1 pixel PNG encoded in base64 for testing image entry endpoints
    self.test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAA/gAAAE4AQMAAADVYspJAAAAA1BMVEUEAgSVKDOdAAAAPUlEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/BicAAABWZX81AAAAABJRU5ErkJggg=="
    
    self.public_image_entry = Entry.objects.create(
        author=self.author,
        title='Public Image',
        content=self.test_image_b64,
        contentType='image/png;base64',
        visibility='PUBLIC',
        description='a public image entry'
    )
    self.private_image_entry = Entry.objects.create(
        author=self.author,
        title='Private Image',
        content=self.test_image_b64,
        contentType='image/png;base64',
        visibility='PRIVATE',
        description='a private image entry'
    )
    self.deleted_image_entry = Entry.objects.create(
        author=self.author,
        title='Deleted Image',
        content=self.test_image_b64,
        contentType='image/png;base64',
        visibility='DELETED',
        description='a deleted image entry'
    )
    self.text_entry = Entry.objects.create(
        author=self.author,
        title='Text Entry',
        content='just some text',
        contentType='text/plain',
        visibility='PUBLIC',
        description='not an image'
    )

  def test_get_public_image_by_serial(self):
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.public_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'image/png')

  def test_get_image_not_found_for_text_entry(self):
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.text_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 404)

  def test_get_private_image_as_stranger(self):
    self.client.login(username='StrangerShrek', password='donkeykongRAAH999')
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 403)

  def test_get_private_image_as_friend(self):
    self.client.login(username='NemoTheFish', password='findingthingslol')
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 200)

  def test_get_deleted_image(self):
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.deleted_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 410)

  def test_get_unauthenticated_private_image(self):
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 403) 

###########################
# READING USER STORY TEST #
##########################
"""
Sources:
- https://www.django-rest-framework.org/api-guide/testing/
- https://docs.djangoproject.com/en/6.0/topics/testing/tools/#the-test-client
- https://docs.djangoproject.com/en/6.0/topics/testing/overview/
- https://docs.djangoproject.com/en/6.0/topics/testing/tools/#the-test-client
Date Accessed: Saturday, Feb. 28, 2026
"""
class StreamAPITest(TestCase):
  
  def setUp(self):
    """Create user1, author and stranger"""
    
    #pretend user we have logged in as
    self.user = Author.objects.create_user(
      username = 'user1test',
      password='user11234',
      displayName = 'User 1 Test',
      is_approved = True,
    )
    
    #An object that is following or friends with the user
    self.author = Author.objects.create_user(
      username = 'author1test',
      password='author11234',
      displayName = 'Author 1 Test',
      is_approved = True,
    )
    
    #an object that has no relationship with the user
    self.stranger = Author.objects.create_user(
      username = 'stranger1test',
      password='stranger11234',
      displayName = 'Stranger 1 Test',
      is_approved = True,
    )
    self.client = Client()
    self.client.login(username='user1test', password='user11234')
    
  
  #Empty
  #stream returns empty list when no entries exists
  def test_empty(self):
    """Tests for when no entries exists"""
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 0)
      
  #stream reruns empty list when only deleted entries exist
  def test_deleted_entries(self):
    """Stream should be empty when they are all have been deleted"""
    
    Entry.objects.create(
      author = self.user,
      title='I regret writing this',
      content='Foul messages in here',
      contentType="text/plain",
      visibility='DELETED',
      description='this is a test under StreamAPITest',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 0)
    
  #AUthentication
    #unaunthenticated user cannot access stream 
  def test_unauthenticated_user(self):
    self.client.logout()
    self.assertEqual(self.client.get('/munch/api/stream/').status_code, 302)
    
  #Test public entries visible to everyone
  
  #public entry from anyone shows
  def test_public_entry(self):
    """Test to ensure entries from anyone set to public is visible"""
    Entry.objects.create(
      author = self.author,
      title = 'Public PSA TEST',
      content = 'I am conducting a public test of my entry. YALL SEE THIS?!',
      contentType = 'text/plain',
      visibility = 'PUBLIC',
      description = 'This entry is a test with public visibility setting',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'Public PSA TEST')
    
  #public entry from stranger shows
  def test_public_entry_stranger(self):
    """Test to ensure entries by stranger set to public is visible to anyone"""
    Entry.objects.create(
      author = self.stranger,
      title = 'Public PSA Test by Stranger',
      content = 'I am conducting a public test of my entry. Im a strange',
      contentType = 'text/plain',
      visibility = 'PUBLIC',
      description = 'This entry is a test using stranger',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'Public PSA Test by Stranger')
  
  #public entries (multiple) can shows
  def test_many_public_entries(self):
    Entry.objects.create(
      author = self.user,
      title = 'Multiple testing by User',
      content = 'I like pizza. Anyone else?',
      contentType = 'text/plain',
      visibility = 'PUBLIC',
      description = 'User entry test for many entries',
    )
    Entry.objects.create(
      author = self.author,
      title = 'Multiple testing by Author',
      content = 'I like pizza',
      contentType = 'text/plain',
      visibility = 'PUBLIC',
      description = 'This entry is a test using author for many entries',
    )
    Entry.objects.create(
      author = self.stranger,
      title = 'Multiple testing by Stranger',
      content = 'I like sushi',
      contentType = 'text/plain',
      visibility = 'PUBLIC',
      description = 'This entry is a test using stranger for many entries',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 3)
    
  #Friends only entries visible to friends ONLY
  def test_private_entry(self):
    """Ensures entries in friends-only visibility is only shown to friends"""
    Entry.objects.create(
      author = self.stranger,
      title = 'Friends only Post by Random',
      content = 'Hidden',
      contentType = 'text/plain',
      visibility = 'PRIVATE',
      description = 'test friends only post',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 0)
  
  def test_one_way_private_entry(self):
    """
    Author follows user but user doesnt follow back.
    Author's private's post should NOT show in user's stream
    because one-way follow is not a friendship.
    """
    Follow.objects.create(
      actor = self.author,
      object = self.user,
      status = 'accepted',
    )
    Entry.objects.create(
      author = self.author,
      title = 'B friends only entry',
      content = 'hidden',
      contentType = 'text/plain',
      visibility = 'PRIVATE',
      description = 'One way friendship test',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 0)
    
  def test_own_entry_public(self):
    """tests user's own entries visibility is shown to them"""
    Entry.objects.create(
      author=self.user,
      title='My Public Post For Me',
      content='Hello World',
      contentType='text/plain',
      visibility='PUBLIC',
      description='test user and their own post'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'My Public Post For Me')

  def test_own_private_entry(self):
    """User's own friends-only entry should appear in stream"""
    Entry.objects.create(
      author=self.user,
      title='My Private Post',
      content='Secret',
      contentType='text/plain',
      visibility='PRIVATE',
      description='test for friends only entries i can see for meself'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'My Private Post')

  def test_own_entry_unlisted(self):
    """Tests User's own unlisted entry appear on their stream"""
    Entry.objects.create(
      author=self.user,
      title='My Unlisted Post for meself',
      content='Hidden',
      contentType='text/plain',
      visibility='UNLISTED',
      description='test for meself unlisted'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'My Unlisted Post for meself')

  # Deleted entries
  def test_own_entry_deleted(self):
    """User's own deleted entry should not be visible"""
    Entry.objects.create(
      author=self.user,
      title='Deleted Post',
      content='Gone',
      contentType='text/plain',
      visibility='DELETED',
      description='test deleted post'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 0)

  def test_author_entry_deleted(self):
      """Other author's deleted entry should not show at all"""
      Entry.objects.create(
          author=self.author,
          title='Author Deleted Post',
          content='Gone',
          contentType='text/plain',
          visibility='DELETED',
          description='test author deleted entry'
      )
      response = self.client.get('/munch/api/stream/')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.json()['src']), 0)

  def test_entry_sort(self):
    """Tests that Entries are sorted from newest"""
    Entry.objects.create(
      author=self.user,
      title='Old Post',
      content='First',
      contentType='text/plain',
      visibility='PUBLIC',
      description='test',
      published=timezone.now() - timedelta(days=2)
    )
    Entry.objects.create(
      author=self.user,
      title='New Post',
      content='Second',
      contentType='text/plain',
      visibility='PUBLIC',
      description='test',
      published=timezone.now()
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    entries = response.json()['src']
    self.assertEqual(len(entries), 2)
    self.assertEqual(entries[0]['title'], 'New Post')
    self.assertEqual(entries[1]['title'], 'Old Post')

  def test_edited_entry_timestamp(self):
    """Edited entry should keep its original published time"""
    original_time = timezone.now() - timedelta(days=5)
    entry = Entry.objects.create(
      author=self.user,
      title='Original Title',
      content='Original',
      contentType='text/plain',
      visibility='PUBLIC',
      description='test',
      published=original_time
    )

    entry.title = 'Edited Title'
    entry.content = 'Updated content'
    entry.save()

    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    entries = response.json()['src']
    self.assertEqual(len(entries), 1)
    self.assertEqual(entries[0]['title'], 'Edited Title')
    # Published time should still be the original time
    self.assertIn(original_time.strftime('%Y-%m-%d'), entries[0]['published'])

  ####################################################
  # VISIBILITY USER STORY TEST THAT RELATES TO STREAM#
  ####################################################
  def test_follower_sees_unlisted_entry(self):
    """Follower should see unlisted entries from someone they follow"""
    Follow.objects.create(
        actor=self.user,
        object=self.author,
        status='accepted'
    )
    Entry.objects.create(
        author=self.author,
        title='A message to all of you my awesome followers',
        content='only my followers can see this so listen up! yall are amazing',
        contentType='text/plain',
        visibility='UNLISTED',
        description='test follower sees unlisted'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['src']), 1)
    self.assertEqual(response.json()['src'][0]['title'], 'A message to all of you my awesome followers')

  def test_friend_sees_private_entry(self):
      """Friend should see friends-only entries from their friend"""
      Follow.objects.create(
          actor=self.user,
          object=self.author,
          status='accepted'
      )
      Follow.objects.create(
          actor=self.author,
          object=self.user,
          status='accepted'
      )
      Entry.objects.create(
          author=self.author,
          title='Private Post by Friend TEST',
          content='top secret info click here',
          contentType='text/plain',
          visibility='PRIVATE',
          description='test entry. friend sees private entry'
      )
      response = self.client.get('/munch/api/stream/')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.json()['src']), 1)
      self.assertEqual(response.json()['src'][0]['title'], 'Private Post by Friend TEST')

###############################     
# VISIBILITY USER STORY TESTS #
###############################
class GetEntryTest(TestCase):

  def setUp(self):
      self.client = Client()
      self.author = Author.objects.create_user(
        username='entry_author',
        password='LETMEINPLEASExoxo',
        displayName='Entry Author',
        is_approved=True
      )
      self.stranger = Author.objects.create_user(
        username='entrystrangerDANGER',
        password='IamNicePerson1',
        displayName='Entry Stranger Danger',
        is_approved=True
      )
      self.unlisted_entry = Entry.objects.create(
        author=self.author,
        title='What Im currently baking: macarons and pain au chocolat :3',
        content='french pastry baking experiment',
        contentType='text/plain',
        visibility='UNLISTED',
        description='test unlisted entry direct access'
      )
      self.deleted_entry = Entry.objects.create(
        author=self.author,
        title='Deleted Entry',
        content='u cant see this, even with ur third eye',
        contentType='text/plain',
        visibility='DELETED',
        description='test deleted entry'
      )

  def test_unlisted_entry_visibility(self):
    
    self.client.login(username='entrystrangerDANGER', password='IamNicePerson1')
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.unlisted_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)

  @unittest.skip("admin logic not yet implemented")
  def test_deleted_entry_visbility_seen_by_admin(self):
  
    admin = Author.objects.create_superuser(
        username='thanos',
        password='igotdapower1111',
        displayName='Admin aka Thanos',
        is_approved=True
    )
    self.client.login(username='thanos', password='igotdapower1111')
    response = self.client.get(
        f'/munch/authors/{self.author.uuid}/entries/{self.deleted_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)

###########################
# SHARING USER STORY TEST #
##########################



#####################################
# FOLLOWING/FRIENDS USER STORY TEST #
####################################



##################################
# COMMENTS/LIKES USER STORY TEST #
#################################
class CommentAPITest(TestCase):

  def setUp(self):
    self.client = APIClient()

    self.author = Author.objects.create_user(
      username='author', password='notOscarWilde',
      displayName='Author', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.friend = Author.objects.create_user(
      username='RealFriend', password='imyouroppfr',
      displayName='RealFriend', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.stranger = Author.objects.create_user(
      username='stranger', password='justalurkerlol',
      displayName='Stranger', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )

    # Make author and friend mutual followers (friends)
    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')

    self.public_entry = Entry.objects.create(
      author=self.author, title='I cant stop eating carbs',
      content='carbs n protein yummy', visibility='PUBLIC'
    )
    self.private_entry = Entry.objects.create(
      author=self.author, title='Found morels in my backyard!',
      content='cant wait to cook these omg im a lucky human indeed', visibility='PRIVATE'
    )

    self.comment = Comment.objects.create(
      author=self.friend,
      entry=self.public_entry,
      comment='Pizza and garlic bread omnomnoms'
    )

  def test_get_entry_comments_public(self):
    response = self.client.get(
      f'/munch/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['type'], 'comments')
    self.assertEqual(response.data['count'], 1)

  def test_get_entry_comments_private_as_stranger(self):
    self.client.login(username='stranger', password='justalurkerlol')
    response = self.client.get(
      f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 403)
  
  def test_get_entry_comments_private_as_friend(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.get(
        f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 200)

  def test_post_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.post(
        f'/munch/api/authors/{self.friend.uuid}/commented/',
        {
          'entry': self.public_entry.fqid,
          'comment': 'hecc yea! WE LOVE CARBS!'
        }
    )
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Comment.objects.filter(comment='hecc yea! WE LOVE CARBS!').exists())

  def test_get_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.get(
      f'/munch/api/authors/{self.friend.uuid}/commented/{self.comment.serial}/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['comment'], 'Pizza and garlic bread omnomnoms')

  def test_get_entry_comments_not_authenticated(self):
    response = self.client.get(f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/')
    self.assertEqual(response.status_code, 403)

  def test_get_comments_on_deleted_entry(self):
    deleted_entry = Entry.objects.create(
      author=self.author, title='Deleted Entry',
      content='gone', visibility='DELETED'
    )
    response = self.client.get(
      f'/munch/api/authors/{self.author.uuid}/entries/{deleted_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 410)

  def test_post_comment_on_deleted_entry(self):
      deleted_entry = Entry.objects.create(
        author=self.author, title='Deleted Entry',
        content='gone', visibility='DELETED'
      )
      self.client.login(username='RealFriend', password='imyouroppfr')
      response = self.client.post(
          f'/munch/api/authors/{self.friend.uuid}/commented/',
          {
            'entry': deleted_entry.fqid,
            'comment': 'hello? is it me youre looking for?? - Lionel Richie'
          }
      )
      self.assertEqual(response.status_code, 410)
class LikeAPITest(TestCase):

  def setUp(self):
    self.client = APIClient()

    self.author = Author.objects.create_user(
      username='JaneAusten', password='notJaneAusten',
      displayName='Emma', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.friend = Author.objects.create_user(
      username='Kerroppi', password='hellokittypochacco',
      displayName='Kekekerroppi', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.stranger = Author.objects.create_user(
      username='AnonymousNotHacker', password='strangerdangeruhOH',
      displayName='NotAHacker', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )

    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')

    self.public_entry = Entry.objects.create(
      author=self.author, title='Public Entry',
      content='Agatha Christie u are so cool', visibility='PUBLIC'
    )
    self.private_entry = Entry.objects.create(
      author=self.author, title='Private Entry',
      content='Sanrio > Disney', visibility='PRIVATE'
    )

    self.comment = Comment.objects.create(
      author=self.friend,
      entry=self.public_entry,
      comment='what the hecc is going on?!'
    )

    self.like = Like.objects.create(
      author=self.friend,
      object_url=self.public_entry.fqid
    )

  def test_get_entry_likes_public(self):
    response = self.client.get(f'/munch/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/likes/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['type'], 'likes')
    self.assertEqual(response.data['count'], 1)

  def test_get_entry_likes_private_as_stranger(self):
    self.client.force_login(self.stranger)
    response = self.client.get(f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/')
    self.assertEqual(response.status_code, 403)

  def test_get_entry_likes_private_as_friend(self):
    self.client.login(username='Kerroppi', password='hellokittypochacco')
    response = self.client.get(f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/')
    self.assertEqual(response.status_code, 200)

  def test_like_entry(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    response = self.client.post(f'/munch/api/authors/{self.stranger.uuid}/liked/', {'object': self.public_entry.fqid})
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.public_entry.fqid).exists())

  def test_like_comment(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    response = self.client.post(
      f'/munch/api/authors/{self.stranger.uuid}/liked/',
      {'object': self.comment.fqid}
    )
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.comment.fqid).exists())

  def test_get_comment_likes(self):
    Like.objects.create(author=self.stranger, object_url=self.comment.fqid)
    response = self.client.get(
      f'/munch/api/authors/{self.friend.uuid}/entries/{self.public_entry.serial}/comments/{self.comment.serial}/likes/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['count'], 1)

  def test_get_like(self):
    response = self.client.get(
      f'/munch/api/authors/{self.friend.uuid}/liked/{self.like.serial}/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['object'], self.public_entry.fqid)


  def test_get_entry_likes_unauthenticated(self):
    response = self.client.get(
      f'/munch/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/'
    )
    self.assertEqual(response.status_code, 403)

  def test_like_spam(self):
      self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
      self.client.post(
        f'/munch/api/authors/{self.stranger.uuid}/liked/',
        {'object': self.public_entry.fqid}
      )
      response = self.client.post(
        f'/munch/api/authors/{self.stranger.uuid}/liked/',
        {'object': self.public_entry.fqid}
      )
      self.assertEqual(response.status_code, 400)

###################################
# NODE MANAGEMENT USER STORY TEST #
##################################