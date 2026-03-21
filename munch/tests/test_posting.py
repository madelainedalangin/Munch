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
  
  # Note: testing create, edit, delete entry tests the UI by checking if pages exist or not
  # which cover the user story: "As an author, I want to be able to use my web-browser to manage/author my entries, so I don't have to use a clunky API."

  # Tests creating an entry by checking if we can access the entry's details page
  # User story: "As an author, I want to make entries, so I can share my thoughts and pictures with other local authors."
  def test_create_entry(self):
    #lets first create an entry 
    entry = self.mockEntry()
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)

  # Tests modifying an entry by checking if the content changed before and after modification
  # User story: "As an author, I want to edit my entries locally, so that I'm not stuck with a typo on a popular entry."
  def test_edit_entry(self):
    entry = self.mockEntry()
    initial_content = entry.content
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    response = self.client.post(
      f"/authors/{self.user.uuid}/entries/{entry.serial}/edit/",
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
  # User Story: "As an author, I want to delete my own entries locally, so I can remove entries that are out of date or made by mistake."
  def test_delete_entry(self):
    entry = self.mockEntry()
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    self.client.post(f'/authors/{self.user.uuid}/entries/{entry.serial}/delete/')
    entry.refresh_from_db()
    self.assertEqual(entry.visibility,"DELETED")
    # check if the page exists after deletion
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 410)

  # Tests if entry is generated in plain or common mark text
  # User story: 
  # - "As an author, entries I make can be in simple plain text, because I don't always want all the formatting features of CommonMark."
  # - "As an author, entries I make can be in CommonMark, so I can give my entries some basic formatting."
  def test_content_text(self):
    # first create an entry plain text 
    entry =  self.mockEntry()
    # assert if we successfully access the entry page
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(entry.contentType, 'text/plain')
    #Convert text to markdown
    response = self.client.post(
      f"/authors/{self.user.uuid}/entries/{entry.serial}/edit/",
      {
        "author": self.user,
        "title": 'Posty posts',
        "content":'#Title ##Subtitle ###type',
        "contentType": "text/markdown",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    entry.refresh_from_db()
    # assert if we successfully access the entry page 
    response = self.client.get(f"/authors/{self.user.uuid}/entries/{entry.serial}/")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(entry.contentType, 'text/markdown')

  # test if another user can edit a user post 
  # User Story: "As an author, other authors cannot modify my entries, so that I don't get impersonated.""
  def test_unauthorized_access(self):
    entry =  self.mockEntry()
    temp_user = Author.objects.create_user(
      username = 'posty2',
      password='ilove8989',
      displayName = 'posty2 the second posty tester!',
      is_approved = True,
    )
    self.client.login(username='posty2', password='ilove8989')
    response = self.client.post(
      f"/authors/{self.user.uuid}/entries/{entry.serial}/edit/",
      {
        "author": self.user,
        "title": 'Posty posts',
        "content":'#Title ##Subtitle ###type',
        "contentType": "text/markdown",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 403)

class PostingAPITest(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.author = Author.objects.create_user(
        username='postyapi',
        password='ilove7676',
        displayName='postyapi the api post',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    self.friend = Author.objects.create_user(
        username='nineninetynine',
        password='percentofgamblersquitbeforehittingbig',
        displayName='gamble',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    self.stranger = Author.objects.create_user(
        username='patience',
        password='isavirtue',
        displayName='ediwauw',
        host=f"{settings.BACKEND_URL}/api/",
        is_approved=True
    )
    self.public_entry = Entry.objects.create(
      author = self.author,
      title='public entry',
      content='this is test for PostingTest',
      contentType="text/plain",
      visibility='PUBLIC',
      description='this is a test under StreamAPITest',
    )
    self.private_entry = Entry.objects.create(
      author = self.author,
      title='private entry',
      content='this is test for PostingTest',
      contentType="text/plain",
      visibility='PRIVATE',
      description='this is a test under StreamAPITest',
    )
    self.deleted_entry = Entry.objects.create(
        author = self.author,
      title='deleted entry',
      content='this is test for PostingTest',
      contentType="text/plain",
      visibility='DELETED',
      description='this is a test under StreamAPITest',
    )

    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')
  
  def test_get_entry_by_author_and_serial(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)
  def test_get_entry_by_author_and_serial_as_friend(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)
  def test_get_entry_by_author_and_serial_as_stranger(self):
    self.client.login(username="patience", password="isavirtue")
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/'
    )
    self.assertEqual(response.status_code, 403) 
  def test_put_entry_by_author_and_serial(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.put(
      f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/',
      {
        "title": 'rahhh',
        "content":'rahh rahh rahh',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 200)
  def test_put_entry_by_author_and_serial_as_not_author(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.put(
      f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/',
      {
        "author": self.author,
        "title": 'rahhh',
        "content":'rahh rahh rahh',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 403)
    
  def test_delete_entry_by_author_and_serial(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.delete(
      f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/'
    )
    self.assertEqual(response.status_code, 204)
    entry = Entry.objects.get(
            author=self.author,
            serial=self.public_entry.serial
        )
    self.assertEqual(entry.visibility, 'DELETED')
  
  def test_delete_entry_by_author_and_serial_as_not_author(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.delete(
      f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/'
    )
    self.assertEqual(response.status_code, 403)
    entry = Entry.objects.get(
            author=self.author,
            serial=self.public_entry.serial
        )
    self.assertNotEqual(entry.visibility, 'DELETED')

  def test_get_entry_by_fqid(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.get(
      f'/api/entries/{self.private_entry.fqid}/'
    )
    self.assertEqual(response.status_code, 200)

  def test_get_entry_by_fqid_as_friend(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.get(
      f'/api/entries/{self.private_entry.fqid}/'
    )
    self.assertEqual(response.status_code, 200)

  def test_get_entry_by_fqid_as_stranger(self):
    self.client.login(username="patience", password="isavirtue")
    response = self.client.get(
      f'/api/entries/{self.private_entry.fqid}/'
    )
    self.assertEqual(response.status_code, 403)

  def test_get_entry_creation(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/'
    )
    self.assertEqual(response.status_code, 200)

    titles = [entry["title"] for entry in response.data["src"]]
    self.assertIn("public entry", titles)
    self.assertIn("private entry", titles)
    self.assertNotIn("deleted entry", titles)

  def test_get_entry_creation_as_stranger(self):
    self.client.login(username="patience", password="isavirtue")
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/'
    )
    self.assertEqual(response.status_code, 200)

    titles = [entry["title"] for entry in response.data["src"]]
    self.assertIn("public entry", titles)
    self.assertNotIn("private entry", titles)
    self.assertNotIn("deleted entry", titles)

  def test_get_entry_creation_as_friend(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/'
    )
    self.assertEqual(response.status_code, 200)

    titles = [entry["title"] for entry in response.data["src"]]
    self.assertIn("public entry", titles)
    self.assertIn("private entry", titles)
    self.assertNotIn("deleted entry", titles)

  def test_post_entry_creation(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.post(
      f'/api/authors/{self.author.uuid}/entries/',
      {
        "title": 'rahhh',
        "content":'rahh rahh rahh',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 201)

  def test_post_entry_creation_with_invalid_form(self):
    self.client.login(username="postyapi", password="ilove7676")
    response = self.client.post(
      f'/api/authors/{self.author.uuid}/entries/',
      {
        "content":'rahh rahh rahh',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 400)

  def test_post_entry_creation_with_invalid_form(self):
    self.client.login(username="nineninetynine", password="percentofgamblersquitbeforehittingbig")
    response = self.client.post(
      f'/api/authors/{self.author.uuid}/entries/',
      {
        "author": self.author,
        "content":'rahh rahh rahh',
        "contentType": "text/plain",
        "visibility": 'PUBLIC',
        "description": 'this is a test under PostingTest',
      }
    )
    self.assertEqual(response.status_code, 403)

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
    self.client.login(username=self.author.username, password='meowUWUniao8')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.public_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'image/png')

  def test_get_image_not_found_for_text_entry(self):
    self.client.login(username=self.author.username, password='meowUWUniao8')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.text_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 404)

  def test_get_private_image_as_stranger(self):
    self.client.login(username='StrangerShrek', password='donkeykongRAAH999')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 403)

  def test_get_private_image_as_friend(self):
    self.client.login(username='NemoTheFish', password='findingthingslol')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 200)

  def test_get_deleted_image(self):
    self.client.login(username=self.author.username, password='meowUWUniao8')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.deleted_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 410)

  def test_get_unauthenticated_private_image(self):
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_image_entry.serial}/image/'
    )
    self.assertEqual(response.status_code, 403) 
