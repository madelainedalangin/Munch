from django.test import TestCase, Client
from munch.models import Author, Entry, Comment, Like, Follow
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from django.urls import reverse
from unittest.mock import patch
from munch.utils import sync_github_activity
from rest_framework.test import APIClient
import unittest

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
        self.assertIn("/api/", self.author.id)
        
        # Check Web URL (web)
        self.assertIn("/authors/", self.author.web)
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
        self.client.login(username='joshua1', password='password123')
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

#Source: Claude Sonnet 4.6
#Prompt: write a test for NoReverseMatch
#Date Accessed: Sunday, March 29, 2026
class SuggestionsPageTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.local_user = Author.objects.create_user(
            username='alice',
            password='password123',
            displayName='Alice',
            is_approved=True
        )
        # Remote author stub — username is None, local uuid may differ from remote FQID
        cls.remote_author = Author.objects.create(
            displayName='Remote Person',
            host='http://othernode.example.com/api/',
            username=None,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='alice', password='password123')

    def test_suggestions_with_remote_author(self):
        """profile-summary.html must not call reverse('public_profile')
        for remote author stubs — username=None is the reliable guard."""
        response = self.client.get(reverse('munch:connect'))
        self.assertEqual(response.status_code, 200)

    def test_profile_summary_weburl_remote_author(self):
        """Remote authors should link to their own node via author.web,
        not a local public_profile URL which would 404 or mismatch uuid."""
        response = self.client.get(reverse('munch:connect'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 
            f"/authors/{self.remote_author.uuid}/")