from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from munch.models import Author, Entry, Comment, Like, Follow, Server
from urllib.parse import quote
import base64

##################################
# COMMENTS/LIKES USER STORY TEST #
#################################
class CommentAPITest(TestCase):

  def setUp(self):
    self.client = APIClient()

    self.author = Author.objects.create_user(
      username='author', password='notOscarWilde',
      displayName='Author', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.friend = Author.objects.create_user(
      username='RealFriend', password='imyouroppfr',
      displayName='RealFriend', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.stranger = Author.objects.create_user(
      username='stranger', password='justalurkerlol',
      displayName='Stranger', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )

    # Make author and friend mutual followers (friends)
    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')

    self.public_entry = Entry.objects.create(
      author=self.author, title='I cant stop eating carbs',
      content='carbs n protein yummy', visibility='PUBLIC'
    )
    self.private_entry = Entry.objects.create(
      author=self.author, title='Found morels in my backyard!',
      content='cant wait to cook these omg im a lucky human indeed', visibility='PRIVATE'
    )

    self.comment = Comment.objects.create(
      author=self.friend,
      entry=self.public_entry,
      comment='Pizza and garlic bread omnomnoms'
    )

    self.node = Server.objects.create(
      url='http://remotenode.com',
      username='remotenode',
      password='nodepassword',
      is_approved=True
    )

  def _node_auth(self):
    credentials = base64.b64encode(b'remotenode:nodepassword').decode('utf-8')
    self.client.credentials(
      HTTP_AUTHORIZATION='Basic ' + credentials,
      HTTP_ORIGIN='http://remotenode.com'
    )

  def test_get_entry_comments_public(self):
    url = reverse('munch:get_entry_comments_by_serial', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.public_entry.serial
    })
    self.client.login(username=self.author.username, password='notOscarWilde')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['type'], 'comments')
    self.assertEqual(response.data['count'], 1)

  def test_get_entry_comments_private_as_stranger(self):
    self.client.login(username='stranger', password='justalurkerlol')
    url = reverse('munch:get_entry_comments_by_serial', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)

  def test_get_entry_comments_private_as_friend(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    url = reverse('munch:get_entry_comments_by_serial', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_post_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    url = reverse('munch:commented', kwargs={'author_serial': self.friend.uuid})
    response = self.client.post(url, {
      'entry': self.public_entry.fqid,
      'comment': 'hecc yea! WE LOVE CARBS!'
    })
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Comment.objects.filter(comment='hecc yea! WE LOVE CARBS!').exists())

  def test_get_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    url = reverse('munch:get_comment_by_serial', kwargs={
      'author_serial': self.friend.uuid,
      'comment_serial': self.comment.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['comment'], 'Pizza and garlic bread omnomnoms')

  def test_get_entry_comments_not_authenticated(self):
    url = reverse('munch:get_entry_comments_by_serial', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)

  def test_get_comments_on_deleted_entry(self):
    deleted_entry = Entry.objects.create(
      author=self.author, title='Deleted Entry',
      content='gone', visibility='DELETED'
    )
    self.client.login(username=self.author.username, password='notOscarWilde')
    url = reverse('munch:get_entry_comments_by_serial', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': deleted_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 410)

  def test_post_comment_on_deleted_entry(self):
    deleted_entry = Entry.objects.create(
      author=self.author, title='Deleted Entry',
      content='gone', visibility='DELETED'
    )
    self.client.login(username='RealFriend', password='imyouroppfr')
    url = reverse('munch:commented', kwargs={'author_serial': self.friend.uuid})
    response = self.client.post(url, {
      'entry': deleted_entry.fqid,
      'comment': 'hello? is it me youre looking for?? - Lionel Richie'
    })
    self.assertEqual(response.status_code, 410)

  def test_remote_comment_inbox(self):
    comment_data = {
      "type": "comment",
      "author": {
        "type": "author",
        "id": "http://remotenode.com/api/authors/111",
        "host": "http://remotenode.com/api/",
        "displayName": "Remote User",
        "github": "",
        "profileImage": "",
        "web": "http://remotenode.com/authors/111",
      },
      "comment": "great post from a remote node!",
      "contentType": "text/plain",
      "published": "2026-06-06T13:07:04+00:00",
      "id": "http://remotenode.com/api/authors/111/commented/130",
      "entry": self.public_entry.fqid,
    }
    self._node_auth()
    url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
    response = self.client.post(url, data=comment_data, format='json')
    #print(response.data)
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Comment.objects.filter(comment='great post from a remote node!').exists())

  def test_remote_comment_on_nonexistent_entry_via_inbox(self):
    comment_data = {
        "type": "comment",
        "author": {
          "type": "author",
          "id": "http://remotenode.com/api/authors/111",
          "host": "http://remotenode.com/api/",
          "displayName": "Remote User",
          "github": "",
          "profileImage": "",
          "web": "http://remotenode.com/authors/111",
        },
      "comment": "hello is anyone there",
      "contentType": "text/plain",
      "published": "2026-06-06T13:07:04+00:00",
      "id": "http://remotenode.com/api/authors/111/commented/999",
      "entry": "http://remotenode.com/api/authors/111/entries/doesnotexist",
    }
    self._node_auth()
    url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
    response = self.client.post(url, data=comment_data, format='json')
    self.assertEqual(response.status_code, 400)

  def test_remote_comment_private_entry_inbox(self):
    comment_data = {
        "type": "comment",
        "author": {
          "type": "author",
          "id": "http://remotenode.com/api/authors/111",
          "host": "http://remotenode.com/api/",
          "displayName": "Remote User",
          "github": "",
          "profileImage": "",
          "web": "http://remotenode.com/authors/111",
        },
      "comment": "sneaking into a private entry",
      "contentType": "text/plain",
      "published": "2026-06-06T13:07:04+00:00",
      "id": "http://remotenode.com/api/authors/111/commented/998",
      "entry": self.private_entry.fqid,
    }
    self._node_auth()
    url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
    response = self.client.post(url, data=comment_data, format='json')
    self.assertEqual(response.status_code, 403)

  def test_local_comment_on_remote_entry(self):
    # Create a remote author and entry stub
    remote_author = Author.objects.create(
        id='http://remotenode.com/api/authors/999',
        host='http://remotenode.com/api/',
        displayName='Remote Author',
        web='http://remotenode.com/authors/999',
    )
    remote_entry = Entry.objects.create(
        author=remote_author,
        title='Remote Entry',
        content='from another node',
        visibility='PUBLIC',
        fqid='http://remotenode.com/api/authors/999/entries/abc123',
    )
    self.client.login(username='RealFriend', password='imyouroppfr')
    url = reverse('munch:commented', kwargs={'author_serial': self.friend.uuid})
    response = self.client.post(url, {
        'entry': remote_entry.fqid,
        'comment': 'nice post from the remote node!'
    })
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Comment.objects.filter(comment='nice post from the remote node!').exists())

  def test_remote_comment_duplicate_ignored(self):
      """Same comment ID sent twice should not create duplicate"""
      comment_data = {
          "type": "comment",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/111",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/111",
          },
          "comment": "duplicate comment test",
          "contentType": "text/plain",
          "published": "2026-06-06T13:07:04+00:00",
          "id": "http://remotenode.com/api/authors/111/commented/777",
          "entry": self.public_entry.fqid,
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      self.client.post(url, data=comment_data, format='json')
      response = self.client.post(url, data=comment_data, format='json')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Comment.objects.filter(fqid='http://remotenode.com/api/authors/111/commented/777').count(), 1)

  def test_remote_comment_missing_fields(self):
      """Comment with missing required fields should return 400"""
      comment_data = {
          "type": "comment",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/111",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/111",
          },
          # missing comment and entry fields
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      response = self.client.post(url, data=comment_data, format='json')
      self.assertEqual(response.status_code, 400)
class LikeAPITest(TestCase):

  def setUp(self):
    self.client = APIClient()

    self.author = Author.objects.create_user(
      username='JaneAusten', password='notJaneAusten',
      displayName='Emma', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.friend = Author.objects.create_user(
      username='Kerroppi', password='hellokittypochacco',
      displayName='Kekekerroppi', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )
    self.stranger = Author.objects.create_user(
      username='AnonymousNotHacker', password='strangerdangeruhOH',
      displayName='NotAHacker', host=f"{settings.BACKEND_URL}/api/",
      is_approved=True
    )

    Follow.objects.create(actor=self.friend, object=self.author, status='accepted')
    Follow.objects.create(actor=self.author, object=self.friend, status='accepted')

    self.public_entry = Entry.objects.create(
      author=self.author, title='Public Entry',
      content='Agatha Christie u are so cool', visibility='PUBLIC'
    )
    self.private_entry = Entry.objects.create(
      author=self.author, title='Private Entry',
      content='Sanrio > Disney', visibility='PRIVATE'
    )

    self.comment = Comment.objects.create(
      author=self.friend,
      entry=self.public_entry,
      comment='what the hecc is going on?!'
    )

    self.like = Like.objects.create(
      author=self.friend,
      object_url=self.public_entry.fqid
    )

    self.node = Server.objects.create(
      url='http://remotenode.com',
      username='remotenode',
      password='nodepassword',
      is_approved=True
    )

  def _node_auth(self):
    credentials = base64.b64encode(b'remotenode:nodepassword').decode('utf-8')
    self.client.credentials(
      HTTP_AUTHORIZATION='Basic ' + credentials,
      HTTP_ORIGIN='http://remotenode.com'
    )

  def test_get_entry_likes_public(self):
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    url = reverse('munch:get_entry_likes', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.public_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['type'], 'likes')
    self.assertEqual(response.data['count'], 1)

  def test_get_entry_likes_private_as_stranger(self):
    self.client.force_login(self.stranger)
    url = reverse('munch:get_entry_likes', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)

  def test_get_entry_likes_private_as_friend(self):
    self.client.login(username='Kerroppi', password='hellokittypochacco')
    url = reverse('munch:get_entry_likes', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_like_entry(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    url = reverse('munch:liked', kwargs={'author_serial': self.stranger.uuid})
    response = self.client.post(url, {'object': self.public_entry.fqid})
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.public_entry.fqid).exists())

  def test_like_comment(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    url = reverse('munch:liked', kwargs={'author_serial': self.stranger.uuid})
    response = self.client.post(url, {'object': self.comment.fqid})
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.comment.fqid).exists())

  def test_get_comment_likes(self):
    Like.objects.create(author=self.stranger, object_url=self.comment.fqid)
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    url = reverse('munch:get_comment_likes', kwargs={
      'author_serial': self.friend.uuid,
      'entry_serial': self.public_entry.serial,
      'comment_fqid': self.comment.fqid
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['count'], 1)

  def test_get_like(self):
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    url = reverse('munch:get_like_by_serial', kwargs={
      'author_serial': self.friend.uuid,
      'like_serial': self.like.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['object'], self.public_entry.fqid)

  def test_get_entry_likes_unauthenticated(self):
    url = reverse('munch:get_entry_likes', kwargs={
      'author_serial': self.author.uuid,
      'entry_serial': self.private_entry.serial
    })
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)

  def test_like_spam(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    url = reverse('munch:liked', kwargs={'author_serial': self.stranger.uuid})
    self.client.post(url, {'object': self.public_entry.fqid})
    response = self.client.post(url, {'object': self.public_entry.fqid})
    self.assertEqual(response.status_code, 400)

  def test_remote_like_inbox(self):
    like_data = {
      "type": "like",
      "author": {
        "type": "author",
        "id": "http://remotenode.com/api/authors/6767",
        "host": "http://remotenode.com/api/",
        "displayName": "Remote User",
        "github": "",
        "profileImage": "",
        "web": "http://remotenode.com/authors/6767",
      },
      "published": "2026-03-09T13:06:07+00:00",
      "id": "http://remotenode.com/api/authors/6767/liked/255",
      "object": self.public_entry.fqid,
    }
    self._node_auth()
    url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
    response = self.client.post(url, data=like_data, format='json')
    #print(response.data)
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(object_url=self.public_entry.fqid).count() >= 1)

  def test_remote_duplicate_like_inbox(self):
      like_data = {
          "type": "like",
          "author": {
            "type": "author",
            "id": "http://remotenode.com/api/authors/6767",
            "host": "http://remotenode.com/api/",
            "displayName": "Remote User",
            "github": "",
            "profileImage": "",
            "web": "http://remotenode.com/authors/6767",
          },
        "published": "2026-03-09T13:06:07+00:00",
        "id": "http://remotenode.com/api/authors/6767/liked/255",
        "object": self.public_entry.fqid,
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      self.client.post(url, data=like_data, format='json')
      response = self.client.post(url, data=like_data, format='json')  # send twice
      self.assertEqual(response.status_code, 400)

  def test_remote_like_comment_inbox(self):
      like_data = {
          "type": "like",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/6767",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/6767",
          },
          "published": "2026-03-09T13:06:07+00:00",
          "id": "http://remotenode.com/api/authors/6767/liked/300",
          "object": self.comment.fqid,
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      response = self.client.post(url, data=like_data, format='json')
      self.assertEqual(response.status_code, 201)
      self.assertTrue(Like.objects.filter(object_url=self.comment.fqid).exists())

  def test_remote_like_on_remote_entry_inbox(self):
    remote_author = Author.objects.create(
      id='http://remotenode.com/api/authors/888',
      host='http://remotenode.com/api/',
      displayName='Remote Author 2',
      web='http://remotenode.com/authors/888',
    )
    remote_entry = Entry.objects.create(
      author=remote_author,
      title='Remote Entry',
      content='from another node',
      visibility='PUBLIC',
      fqid='http://remotenode.com/api/authors/888/entries/xyz456',
    )
    like_data = {
      "type": "like",
      "author": {
        "type": "author",
        "id": "http://remotenode.com/api/authors/6767",
        "host": "http://remotenode.com/api/",
        "displayName": "Remote User",
        "github": "",
        "profileImage": "",
        "web": "http://remotenode.com/authors/6767",
      },
      "published": "2026-03-09T13:06:07+00:00",
      "id": "http://remotenode.com/api/authors/6767/liked/400",
      "object": remote_entry.fqid,
    }
    self._node_auth()
    url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
    response = self.client.post(url, data=like_data, format='json')
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(object_url=remote_entry.fqid).exists())

  def test_remote_like_comment_duplicate_inbox(self):
      """Same comment like sent twice should return 400"""
      like_data = {
          "type": "like",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/6767",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/6767",
          },
          "published": "2026-03-09T13:06:07+00:00",
          "id": "http://remotenode.com/api/authors/6767/liked/301",
          "object": self.comment.fqid,
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      self.client.post(url, data=like_data, format='json')
      response = self.client.post(url, data=like_data, format='json')
      self.assertEqual(response.status_code, 400)

  def test_remote_like_missing_object_inbox(self):
      """Like with missing object field should return 400"""
      like_data = {
          "type": "like",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/6767",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/6767",
          },
          "published": "2026-03-09T13:06:07+00:00",
          "id": "http://remotenode.com/api/authors/6767/liked/302",
          # missing object field
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      response = self.client.post(url, data=like_data, format='json')
      self.assertEqual(response.status_code, 400)

  def test_remote_like_nonexistent_entry_inbox(self):
      """Like on a nonexistent entry FQID should still be stored"""
      like_data = {
          "type": "like",
          "author": {
              "type": "author",
              "id": "http://remotenode.com/api/authors/6767",
              "host": "http://remotenode.com/api/",
              "displayName": "Remote User",
              "github": "",
              "profileImage": "",
              "web": "http://remotenode.com/authors/6767",
          },
          "published": "2026-03-09T13:06:07+00:00",
          "id": "http://remotenode.com/api/authors/6767/liked/303",
          "object": "http://remotenode.com/api/authors/999/entries/doesnotexist",
      }
      self._node_auth()
      url = reverse('munch:inbox', kwargs={'target_serial': self.author.uuid})
      response = self.client.post(url, data=like_data, format='json')
      self.assertEqual(response.status_code, 201)