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
