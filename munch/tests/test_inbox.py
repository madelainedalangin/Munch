from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from munch.models import *
from munch.serializers import *

from unittest import skip

# INBOX TEST CASES

class InboxAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.alice_local = Author.objects.create_user(
            username='alice',
            password='123',
            displayName='Alice',
            is_approved=True
        )

        cls.bob_remote_data = {
            'type': 'author',
            'id': 'http://remotenode/api/authors/2051213d-d4b4-4cf9-ba57-f2922b39dfa9',
            'web': 'http://remotenode/authors/2051213d-d4b4-4cf9-ba57-f2922b39dfa9',
            'displayName':'Bob',
            'github': None,
            'profileImage': None
        }

        cls.url = reverse('munch:inbox', kwargs={'target_serial': cls.alice.uuid})

    @skip('fix authors model first')
    def test_post_follow(self):

        remote_api_follow = {
            'type': 'follow',
            'summary': 'Bob wants to follow Alice',
            'actor': self.bob_remote_data,
            'object': AuthorSerializer(self.alice_local).validated_data
        }

        response = self.client.post(self.url, remote_api_follow, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if a stub for bob was created
        bob_stub = Author.objects.filter(id='http://remotenode/api/authors/2051213d-d4b4-4cf9-ba57-f2922b39dfa9')
        self.assertTrue(bob_stub.exists())

        # check if follow request was created
        self.assertTrue(Follow.objects.filter(actor=bob_stub, object=self.alice_local))

    @skip('fix authors model first')
    def test_post_entry(self):
        pass

    @skip('fix authors model first')
    def test_post_like(self):
        pass

    @skip('fix authors model first')
    def test_post_comment(self):
        pass