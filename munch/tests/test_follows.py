from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient
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

class FollowAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.alice = Author.objects.create_user(
            username='test_author',
            password='123',
            displayName='test author',
            is_approved=True
        )