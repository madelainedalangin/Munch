from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from munch.models import Author, Entry, Comment, Like, Follow
from urllib.parse import quote

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
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 403)
  
  def test_get_entry_comments_private_as_friend(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.get(
        f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 200)

  def test_post_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.post(
        f'/api/authors/{self.friend.uuid}/commented/',
        {
          'entry': self.public_entry.fqid,
          'comment': 'hecc yea! WE LOVE CARBS!'
        }
    )
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Comment.objects.filter(comment='hecc yea! WE LOVE CARBS!').exists())

  def test_get_comment(self):
    self.client.login(username='RealFriend', password='imyouroppfr')
    response = self.client.get(
      f'/api/authors/{self.friend.uuid}/commented/{self.comment.serial}/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['comment'], 'Pizza and garlic bread omnomnoms')

  def test_get_entry_comments_not_authenticated(self):
    response = self.client.get(f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/comments/')
    self.assertEqual(response.status_code, 403)

  def test_get_comments_on_deleted_entry(self):
    deleted_entry = Entry.objects.create(
      author=self.author, title='Deleted Entry',
      content='gone', visibility='DELETED'
    )
    self.client.login(username=self.author.username, password='notOscarWilde')
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/{deleted_entry.serial}/comments/'
    )
    self.assertEqual(response.status_code, 410)

  def test_post_comment_on_deleted_entry(self):
      deleted_entry = Entry.objects.create(
        author=self.author, title='Deleted Entry',
        content='gone', visibility='DELETED'
      )
      self.client.login(username='RealFriend', password='imyouroppfr')
      response = self.client.post(
          f'/api/authors/{self.friend.uuid}/commented/',
          {
            'entry': deleted_entry.fqid,
            'comment': 'hello? is it me youre looking for?? - Lionel Richie'
          }
      )
      self.assertEqual(response.status_code, 410)
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

  def test_get_entry_likes_public(self):
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    response = self.client.get(f'/api/authors/{self.author.uuid}/entries/{self.public_entry.serial}/likes/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['type'], 'likes')
    self.assertEqual(response.data['count'], 1)

  def test_get_entry_likes_private_as_stranger(self):
    self.client.force_login(self.stranger)
    response = self.client.get(f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/')
    self.assertEqual(response.status_code, 403)

  def test_get_entry_likes_private_as_friend(self):
    self.client.login(username='Kerroppi', password='hellokittypochacco')
    response = self.client.get(f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/')
    self.assertEqual(response.status_code, 200)

  def test_like_entry(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    response = self.client.post(f'/api/authors/{self.stranger.uuid}/liked/', {'object': self.public_entry.fqid})
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.public_entry.fqid).exists())

  def test_like_comment(self):
    self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
    response = self.client.post(
      f'/api/authors/{self.stranger.uuid}/liked/',
      {'object': self.comment.fqid}
    )
    self.assertEqual(response.status_code, 201)
    self.assertTrue(Like.objects.filter(author=self.stranger, object_url=self.comment.fqid).exists())

  def test_get_comment_likes(self):
    Like.objects.create(author=self.stranger, object_url=self.comment.fqid)
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    response = self.client.get(
      f'/api/authors/{self.friend.uuid}/entries/{self.public_entry.serial}/comments/{quote(self.comment.fqid, safe="")}/likes/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['count'], 1)

  def test_get_like(self):
    self.client.login(username=self.stranger.username, password='strangerdangeruhOH')
    response = self.client.get(
      f'/api/authors/{self.friend.uuid}/liked/{self.like.serial}/'
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['object'], self.public_entry.fqid)


  def test_get_entry_likes_unauthenticated(self):
    response = self.client.get(
      f'/api/authors/{self.author.uuid}/entries/{self.private_entry.serial}/likes/'
    )
    self.assertEqual(response.status_code, 403)

  def test_like_spam(self):
      self.client.login(username='AnonymousNotHacker', password='strangerdangeruhOH')
      self.client.post(
        f'/api/authors/{self.stranger.uuid}/liked/',
        {'object': self.public_entry.fqid}
      )
      response = self.client.post(
        f'/api/authors/{self.stranger.uuid}/liked/',
        {'object': self.public_entry.fqid}
      )
      self.assertEqual(response.status_code, 400)