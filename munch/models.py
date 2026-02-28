from django.db import models
from datetime import datetime
import uuid

# possible tables needed for project
host = "127.0.0.1:8000"

class Author(models.Model):
    username = models.CharField(max_length=200)
    displayName = models.CharField(max_length=200)

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    # override save to generate fqid from serial if no fqid is provided
    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"https://{host}/munch/api/authors/{self.serial}"
        return super().save(*args, **kwargs)

class Entry(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)
    visibility = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.TextField()

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"https://{host}/munch/api/authors/{self.author.serial}/entries/{self.serial}"
        return super().save(*args, **kwargs)

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)
    contentType = models.CharField(max_length=200)
    comment = models.TextField()

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"https://{host}/munch/api/authors/{self.author.serial}/commented/{self.serial}"
        return super().save(*args, **kwargs)

class Like(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object = models.ForeignKey(Entry, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"https://{host}/munch/api/authors/{self.author.serial}/liked/{self.serial}"
        return super().save(*args, **kwargs)

class Follow(models.Model):
    actor = models.ForeignKey(Author, on_delete=models.CASCADE,related_name="following")
    object = models.ForeignKey(Author, on_delete=models.CASCADE,related_name="followers")
