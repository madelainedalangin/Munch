from django.db import models
from datetime import datetime
import uuid

# possible tables needed for project

class Author(models.Model):
    serial = models.UUIDField(default=uuid.uuid4)
    username = models.CharField(max_length=200)
    displayName = models.CharField(max_length=200)

class Entry(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)
    visibility = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.TextField()

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)
    contentType = models.CharField(max_length=200)
    comment = models.TextField()

class Like(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object = models.ForeignKey(Entry, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)

class Follow(models.Model):
    actor = models.ForeignKey(Author, on_delete=models.CASCADE)
    object = models.ForeignKey(Author, on_delete=models.CASCADE)
