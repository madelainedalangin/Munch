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

###############################     
# VISIBILITY USER STORY TESTS #
###############################
class GetEntryTest(TestCase):

  def setUp(self):
    self.client = Client()
    
    # User profiles
    self.author1 = Author.objects.create_user(
      username='author1',
      password='LETMEINPLEASExoxo',
      displayName='Author Test 1',
      is_approved=True
    )
    self.author2 = Author.objects.create_user(
      username='author2',
      password='IamNicePerson1',
      displayName='Author Test 2',
      is_approved=True
    )
    
    # Different entries
    self.public_entry = Entry.objects.create(
      author=self.author1,
      title='Everyone can see this post',
      content='As long as you have an account, you can see this. Imagine that.',
      contentType='text/plain',
      visibility='PUBLIC',
      description='Test public entry visibility'
    )
    self.private_entry = Entry.objects.create(
      author=self.author1,
      title='If you are not my friend, you cannot see this',
      content='You are NOT cool enough for me',
      contentType='text/plain',
      visibility='PRIVATE',
      description='Test private entry visibility'
    )
    self.unlisted_entry = Entry.objects.create(
      author=self.author1,
      title='You have to be in the know, or know someone who knows',
      content='Either you love me, or you know someone who loves me, to see this',
      contentType='text/plain',
      visibility='UNLISTED',
      description='Test unlisted entry visibility'
    )
    self.deleted_entry = Entry.objects.create(
      author=self.author1,
      title='Deleted Entry',
      content='You cannot see this, even with your third eye',
      contentType='text/plain',
      visibility='DELETED',
      description='Test deleted entry visibility'
    )

  # Standard user visibility tests

  # Public entries testing
  def test_public_direct_entry_visibility(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.public_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)

  def test_public_stream_entry_visibility(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/stream/'
    )
    self.assertEqual(response.status_code, 200)
    # Check that the public entry is in the stream results
    entry_fqids = [entry['id'] for entry in response.json()['src']]
    self.assertIn(str(self.public_entry.fqid), entry_fqids)


  # Private entries testing
  def test_private_direct_entry_visibility_when_not_friends(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.private_entry.serial}/'
    )
    self.assertEqual(response.status_code, 403)

  def test_private_direct_entry_visibility_when_friends(self):
    self.client.login(username='author2', password='IamNicePerson1')
    # Author 2 sends a request to Author 1, is considered a follower but not friend
    Follow.objects.create(
      actor=self.author2,
      object=self.author1,
      status='accepted'
    )
    # Author 1 follows back Author 2, making them friends
    Follow.objects.create(
      actor=self.author1,
      object=self.author2,
      status='accepted'
    )
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.private_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)

  def test_private_stream_entry_visibility_when_not_friends(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/stream/'
    )
    self.assertEqual(response.status_code, 200)
    # Check that the private entry is not in the stream results
    entry_fqids = [entry['id'] for entry in response.json()['src']]
    self.assertNotIn(str(self.private_entry.fqid), entry_fqids)

  def test_private_stream_entry_visibility_when_friends(self):
    self.client.login(username='author2', password='IamNicePerson1')
    # Author 2 sends a request to Author 1, is considered a follower but not friend
    Follow.objects.create(
      actor=self.author2,
      object=self.author1,
      status='accepted'
    )
    # Author 1 follows back Author 2, making them friends
    Follow.objects.create(
      actor=self.author1,
      object=self.author2,
      status='accepted'
    )
    response = self.client.get(
        f'/api/stream/'
    )
    self.assertEqual(response.status_code, 200)
    # Check that the private entry is in the stream results
    entry_fqids = [entry['id'] for entry in response.json()['src']]
    self.assertIn(str(self.private_entry.fqid), entry_fqids)


  # Unlisted entries testing
  def test_unlisted_direct_entry_visibility(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.unlisted_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)

  def test_unlisted_stream_entry_visibility_when_not_following(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/stream/'
    )
    self.assertEqual(response.status_code, 200)
    # Check that the unlisted entry is not in the stream results
    entry_fqids = [entry['id'] for entry in response.json()['src']]
    self.assertNotIn(str(self.unlisted_entry.fqid), entry_fqids)

  def test_unlisted_stream_entry_visibility_when_following(self):
    self.client.login(username='author2', password='IamNicePerson1')
    # Author 2 sends a request to Author 1, is considered a follower but not friend
    Follow.objects.create(
      actor=self.author2,
      object=self.author1,
      status='accepted'
    )
    response = self.client.get(
        f'/api/stream/'
    )
    self.assertEqual(response.status_code, 200)
    # Check that the unlisted entry is in the stream results
    entry_fqids = [entry['id'] for entry in response.json()['src']]
    self.assertIn(str(self.unlisted_entry.fqid), entry_fqids)


  # Visibility tests as a non-superuser / non-admin user
  def test_deleted_direct_entry_visibility_when_not_admin(self):
    self.client.login(username='author2', password='IamNicePerson1')
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.deleted_entry.serial}/'
    )
    self.assertEqual(response.status_code, 410)


  # Visibility tests as a superuser / admin user
  def test_deleted_direct_entry_visbility_when_admin(self):
    Author.objects.create_superuser(
      username='admin', password='AllSeeingEye', displayName='Admin User'
    )
    self.client.login(username='admin', password='AllSeeingEye')
    response = self.client.get(
        f'/api/authors/{self.author1.uuid}/entries/{self.deleted_entry.serial}/'
    )
    self.assertEqual(response.status_code, 200)
    