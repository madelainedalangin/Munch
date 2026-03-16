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

        cls.url = reverse('munch:manage_following', kwargs={'author_serial': cls.alice.uuid, 'target_FQID': cls.bob.id})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_post(self):
        self.client.login(username='alice', password='123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_no_follow(self):
        self.client.login(username='alice', password='123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_requesting(self):
        self.client.login(username='alice', password='123')

        Follow.objects.create(
            actor=self.alice,
            object=self.bob,
            status='requesting'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_accepted(self):
        self.client.login(username='alice', password='123')

        Follow.objects.create(
            actor=self.alice,
            object=self.bob,
            status='accepted'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_accepted(self):
        self.client.login(username='alice', password='123')

        Follow.objects.create(
            actor=self.alice,
            object=self.bob,
            status='accepted'
        )

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_no_follow(self):
        self.client.login(username='alice', password='123')

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_put_create_new(self):
        self.client.login(username='alice', password='123')

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        follow_alice_bob = Follow(
            actor=self.alice,
            object=self.bob,
            status='accepted'
        )

        self.assertEqual(response.data, FollowRequestSerializer(follow_alice_bob).data)

    def test_put_existing(self):
        self.client.login(username='alice', password='123')

        Follow.objects.create(
            actor=self.alice,
            object=self.bob,
            status='accepted'
        )

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        cls.url = reverse('munch:manage_follower', kwargs={'author_serial': cls.alice.uuid})

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

        cls.url = reverse('munch:get_follow_requests', kwargs={'author_serial': cls.alice.uuid})

    def test_no_follow_requests(self):
        self.client.login(username='alice', password='123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_request_list(self):

        Follow.objects.create(
            actor=self.bob,
            object=self.alice,
            status='requesting'
        )

        Follow.objects.create(
            actor=self.eddie,
            object=self.alice,
            status='requesting'
        )

        self.client.login(username='alice', password='123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(AuthorSerializer(self.bob).data, response.data)
        self.assertIn(AuthorSerializer(self.eddie).data, response.data)
