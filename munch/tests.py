from django.test import TestCase, Client
from .models import Author, Entry, Follow
from django.utils import timezone
from datetime import timedelta

# Create your tests here.

############################
# IDENTITY USER STORY TEST #
###########################

class AuthorTest(TestCase):
  #test for duplicate username not allowed
  pass



###########################
# POSTING USER STORY TEST #
##########################



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
    self.assertEqual(len(response.json()), 0)
      
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
    self.assertEqual(len(response.json()), 0)
    pass
    
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
    self.assertEqual(len(response.json()), 1)
    self.assertEqual(response.json()[0]['title'], 'Public PSA TEST')
    
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
    self.assertEqual(len(response.json()), 1)
    self.assertEqual(response.json()[0]['title'], 'Public PSA Test by Stranger')
  
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
    self.assertEqual(len(response.json()), 3)
    
  #Friends only entries visible to friends ONLY
  def test_friends_only_entry(self):
    """Ensures entries in friends-only visibility is only shown to friends"""
    Entry.objects.create(
      author = self.stranger,
      title = 'Friends only Post by Random',
      content = 'Hidden',
      contentType = 'text/plain',
      visibility = 'FRIENDS',
      description = 'test friends only post',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()), 0)
  
  def test_one_way_friends_entry(self):
    """
    Ensures one-way follow (A -> B) and B's friends-only post shows to A
    but B's friends-only post is not shown to A
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
      visibility = 'FRIENDS',
      description = 'One way friendship test',
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()), 0)
    
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
    self.assertEqual(len(response.json()), 1)
    self.assertEqual(response.json()[0]['title'], 'My Public Post For Me')

  def test_own_entry_friends(self):
    """User's own friends-only entry should appear in stream"""
    Entry.objects.create(
      author=self.user,
      title='My Private Post',
      content='Secret',
      contentType='text/plain',
      visibility='FRIENDS',
      description='test for friends only entries i can see for meself'
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()), 1)
    self.assertEqual(response.json()[0]['title'], 'My Private Post')

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
    self.assertEqual(len(response.json()), 1)
    self.assertEqual(response.json()[0]['title'], 'My Unlisted Post for meself')

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
    self.assertEqual(len(response.json()), 0)

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
      self.assertEqual(len(response.json()), 0)

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
    entries = response.json()
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
    entries = response.json()
    self.assertEqual(len(entries), 1)
    self.assertEqual(entries[0]['title'], 'Edited Title')
    # Published time should still be the original time
    self.assertIn(original_time.strftime('%Y-%m-%d'), entries[0]['published'])

##############################
# VISIBILITY USER STORY TEST #
#############################

class GetEntryTest(TestCase):
  pass


###########################
# SHARING USER STORY TEST #
##########################



#####################################
# FOLLOWING/FRIENDS USER STORY TEST #
####################################



##################################
# COMMENTS/LIKES USER STORY TEST #
#################################



###################################
# NODE MANAGEMENT USER STORY TEST #
##################################