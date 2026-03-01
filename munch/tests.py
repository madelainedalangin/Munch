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
  
  def setup_test_user(self):
    #create user1, author and stranger
    #log in as user1
    pass
  
    #Empty
    #stream returns empty list when no entries exists
    #stream reruns empty list when only deleted entries exist
    
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