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
    