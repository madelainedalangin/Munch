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
# SHARING USER STORY TEST #
##########################

#The following tests from Google, Gemini, "Django Sharing Tests", 03-15-26 -->
class SharingUserStoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create unique UUIDs
        self.uuid_a = uuid.uuid4()
        self.uuid_b = uuid.uuid4()
        
        # Create unique serials for entries
        self.serial_public = uuid.uuid4()
        self.serial_unlisted = uuid.uuid4()
        self.serial_private = uuid.uuid4()
        
        # Create authors
        self.author_a = Author.objects.create(
            username="author_a", 
            uuid=self.uuid_a,
            displayName="Author A"
        )
        self.author_b = Author.objects.create(
            username="author_b", 
            uuid=self.uuid_b,
            displayName="Author B"
        )
        
        # Create entries using valid UUIDs for the serial field
        self.public_entry = Entry.objects.create(
            author=self.author_a, 
            title="Public Post", 
            visibility="PUBLIC", 
            serial=self.serial_public
        )
        self.unlisted_entry = Entry.objects.create(
            author=self.author_a, 
            title="Unlisted Post", 
            visibility="UNLISTED", 
            serial=self.serial_unlisted
        )
        self.private_entry = Entry.objects.create(
            author=self.author_a, 
            title="Private Post", 
            visibility="PRIVATE", 
            serial=self.serial_private
        )

    ## --- Tests for User Story: Shareable Links ---

    def test_logged_in_user_can_view_public_entry_via_link(self):
        self.client.force_login(self.author_b)
        url = reverse('munch:display_entry_by_serial', kwargs={
            'author_id': str(self.author_a.uuid), 
            'entry_serial': str(self.public_entry.serial)
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Post")

    def test_logged_in_user_can_view_unlisted_entry_via_link(self):
        self.client.force_login(self.author_b)
        url = reverse('munch:display_entry_by_serial', kwargs={
            'author_id': str(self.author_a.uuid), 
            'entry_serial': str(self.unlisted_entry.serial)
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unlisted Post")

    def test_logged_in_user_cannot_view_private_entry_without_friendship(self):
        self.client.force_login(self.author_b)
        url = reverse('munch:display_entry_by_serial', kwargs={
            'author_id': str(self.author_a.uuid), 
            'entry_serial': str(self.private_entry.serial)
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    ## --- Tests for User Story: Browse Public Entries ---

    def test_public_browse_shows_all_public_posts(self):
        self.client.force_login(self.author_b)
        url = reverse('munch:public_browse')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Post")
        self.assertNotContains(response, "Unlisted Post")
        self.assertNotContains(response, "Private Post")