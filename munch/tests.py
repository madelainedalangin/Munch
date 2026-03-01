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
    )
    
    #An object that is following or friends with the user
    self.author = Author.objects.create_user(
      username = 'author1test',
      password='author11234',
      displayName = 'Author 1 Test',
    )
    
    #an object that has no relationship with the user
    self.stranger = Author.objects.create_user(
      username = 'stranger1test',
      password='stranger11234',
      displayName = 'Stranger 1 Test',
    )
    self.client = Client()
    self.client.login(username='user1test', password='user11234')
    
  
  #Empty
  #stream returns empty list when no entries exists
  def test_empty_only(self):
    """Tests for when no entries exists"""
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()), 0)
      
  #stream reruns empty list when only deleted entries exist
  def test_deleted_entries_only(self):
    """Stream should be empty when they are all have been deleted"""
    
    Entry.objects.create(
      author = self.user,
      title="I regret writing this",
      content="Foul messages in here",
      contentType="text/plain",
      visibility="DELETED",
      description="this is a test under StreamAPITest"
    )
    response = self.client.get('/munch/api/stream/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()), 0)
    pass
    
  #AUthentication
    #unaunthenticated user cannot access stream 
    
  #Test public entries visible to everyone
    #public entry from anyone shows
    #public entry from stranger shows
    #public entries (multiple) can shows
    
  #Friends only entries visible to friends ONLY
    #friends-only entry from stranger is hidden
    #Test for when Bob follows Alice (Accepted)
    #But ALice has not yet followed back and Bob makes a friends-only post
    #Alice shouldnt be able to see it
      
  # User's own entries always visible
    # user's public entry shows
    # user's private entry shows
    # user's unlisted entry shows
      
  # Deleted entries
    #user's own deleted entry hidden
    #user2's deleted entry hidden
  
  # Sorting
    # entries sorted newest first
    #edited entry shows OG published time
  pass
class StreamViewTest(TestCase):
  pass

class GetEntryTest(TestCase):
  pass

##############################
# VISIBILITY USER STORY TEST #
#############################




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