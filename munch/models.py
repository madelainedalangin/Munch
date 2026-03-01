from django.db import models
from datetime import datetime
import uuid
from django.contrib.auth.models import AbstractUser

# possible tables needed for project
host = "127.0.0.1:8000"

# The following class from Google, Gemini, "Django Author Identity", 02-28-2026
class Author(AbstractUser):
    # Primary Key is a URL (the FQID)
    id = models.URLField(primary_key=True, max_length=500)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    host = models.URLField(default="http://127.0.0.1:8000/")
    displayName = models.CharField(max_length=255)
    github = models.URLField(blank=True, null=True)
    profileImage = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text="Tell us about yourself")

    REQUIRED_FIELDS = ['displayName']


    def save(self, *args, **kwargs):
        # Ensure UUID is generated before we build the FQID
        if not self.uuid:
            import uuid
            self.uuid = uuid.uuid4()
            
        if not self.id:
            # Construct the FQID: http://host/munch/authors/uuid
            # Ensure host ends with a slash for clean URL construction
            base_host = self.host if self.host.endswith('/') else f"{self.host}/"
            self.id = f"{base_host}munch/authors/{self.uuid}"
            
        super().save(*args, **kwargs)

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
            base_host = self.author.host if self.author.host.endswith('/') else f"{self.author.host}/"
            self.fqid = f"{base_host}munch/api/authors/{self.author.uuid}/entries/{self.serial}"
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
    # The person DOING the following
    actor = models.ForeignKey(
        'Author', 
        on_delete=models.CASCADE, 
        related_name='following_relations' # Changed from default
    )
    
    # The person BEING followed
    object = models.ForeignKey(
        'Author', 
        on_delete=models.CASCADE, 
        related_name='follower_relations' # Changed from default
    )
    
    # Optional: ensure an author can't follow the same person twice
    class Meta:
        unique_together = ('actor', 'object')
