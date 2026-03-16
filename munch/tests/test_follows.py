from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from munch.models import Author, Entry, Comment, Like, Follow
from datetime import timedelta
import uuid
from unittest.mock import patch
from munch.utils import sync_github_activity

import unittest

#####################################
# FOLLOWING/FRIENDS USER STORY TEST #
####################################

class GetFollowingTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        self.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        self.eddie = Author.objects.create_user(
            username='eddie',
            password='123',
            displayName='Eddie',
            is_approved=True
        )


        
        self.url = reverse('munch:get_following', kwargs={'author_serial': self.alice.uuid})

    def test_get_following(self):
        pass

    def test_unauthenticated(self):
        pass


class ManageFollowingTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        self.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        self.url = reverse('munch:manage_following', kwargs={'author_serial': self.alice.uuid, 'target_fqid': self.bob.id})

class ManageFollowerTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        self.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        self.url = reverse('munch:manage_follower', kwargs={'author_serial': self.alice.uuid, 'target_fqid': self.bob.id})

class GetFollowRequestsTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        self.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        self.url = reverse('munch:get_follow_requests', kwargs={'author_serial': self.alice.uuid})
