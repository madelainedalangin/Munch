from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from munch.models import Author, Follow
from munch.serializers import AuthorSerializer, FollowRequestSerializer

import unittest

#####################################
# FOLLOWING/FRIENDS USER STORY TEST #
####################################

class GetFollowingTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        cls.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        cls.eddie = Author.objects.create_user(
            username='eddie',
            password='123',
            displayName='Eddie',
            is_approved=True
        )

        cls.url = reverse('munch:get_following', kwargs={'author_serial': cls.alice.uuid})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
    def test_no_following(self):
        self.client.login(username='alice', password='123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_following_list(self):

        follow_alice_bob = Follow.objects.create(
            actor=self.alice,
            object=self.bob,
            status='accepted'
        )

        follow_alice_eddie = Follow.objects.create(
            actor=self.alice,
            object=self.eddie,
            status='accepted'
        )

        self.client.login(username='alice', password='123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(AuthorSerializer(self.bob).data, response.data)
        self.assertIn(AuthorSerializer(self.eddie).data, response.data)

class ManageFollowingTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        cls.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        cls.eddie = Author.objects.create_user(
            username='eddie',
            password='123',
            displayName='Eddie',
            is_approved=True
        )

        cls.url = reverse('munch:get_following', kwargs={'author_serial': cls.alice.uuid})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    

class ManageFollowerTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        cls.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        cls.eddie = Author.objects.create_user(
            username='eddie',
            password='123',
            displayName='Eddie',
            is_approved=True
        )

        cls.url = reverse('munch:get_following', kwargs={'author_serial': cls.alice.uuid})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

class GetFollowRequestsTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.alice = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        cls.bob = Author.objects.create_user(
            username='bob',
            password='123',
            displayName='Bob',
            is_approved=True
        )

        cls.eddie = Author.objects.create_user(
            username='eddie',
            password='123',
            displayName='Eddie',
            is_approved=True
        )

        cls.url = reverse('munch:get_following', kwargs={'author_serial': cls.alice.uuid})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
