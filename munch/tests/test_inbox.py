from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from munch.models import *
from munch.serializers import *

from unittest import skip
import base64

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
            'id': 'http://remotenode.herokuapp.com/api/authors/2051213d-d4b4-4cf9-ba57-f2922b39dfa9',
            'host': 'http://remotenode.herokuapp.com/api/',
            'displayName':'Bob',
            'github': None,
            'profileImage': None,
            'web': 'http://remotenode.herokuapp.com/authors/2051213d-d4b4-4cf9-ba57-f2922b39dfa9'
        }

        cls.remote_server_approved = Server.objects.create(
            url = 'http://remotenode.herokuapp.com',
            username = 'remote',
            password = '123',
            is_approved = True
        )

        cls.url = reverse('munch:inbox', kwargs={'target_serial': cls.alice_local.uuid})

    def basic_auth_header(self, username, password):
        login = base64.b64encode(
            f"{username}:{password}".encode('utf-8')
        ).decode('utf-8')

        return f"Basic {login}"

    def test_post_follow(self):
        
        remote_api_follow = {
            'type': 'follow',
            'summary': 'Bob wants to follow Alice',
            'actor': self.bob_remote_data,
            'object': AuthorSerializer(self.alice_local).data
        }

        self.client.credentials(
            HTTP_ORIGIN = self.remote_server_approved.url,
            HTTP_AUTHORIZATION = self.basic_auth_header(
                self.remote_server_approved.username, 
                self.remote_server_approved.password
            )
        )

        response = self.client.post(self.url, data=remote_api_follow, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if a stub for bob was created
        bob_stub_query = Author.objects.filter(id=self.bob_remote_data.get('id'))
        self.assertTrue(bob_stub_query.exists())
        bob_stub = bob_stub_query.first()
        self.assertIsNone(bob_stub.username)

        # check if follow request was created
        self.assertTrue(Follow.objects.filter(actor=bob_stub, object=self.alice_local).exists())

    @skip('not implemented yet')
    def test_post_entry(self):
        pass

    @skip('note implemented yet')
    def test_post_like(self):
        pass

    @skip('not implemented yet')
    def test_post_comment(self):
        pass