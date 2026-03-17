from django.db import models
from datetime import datetime
import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import markdown

# The following class from Google, Gemini, "Django Author Identity", 02-28-2026
class Author(AbstractUser):
    # Primary Key is a URL (the FQID)
    id = models.URLField(primary_key=True, max_length=500)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    host = models.URLField(default=f"{settings.BACKEND_URL}/api/")
    displayName = models.CharField(max_length=255)
    github = models.URLField(blank=True, null=True)
    profileImage = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text="Tell us about yourself")
    is_approved = models.BooleanField(default=False)
    web = models.URLField(blank=True, unique=True)

    REQUIRED_FIELDS = ['displayName']


    def save(self, *args, **kwargs):
        # Ensure UUID is generated before we build the FQID
        if not self.uuid:
            import uuid
            self.uuid = uuid.uuid4()
            
        if not self.id:
            # Construct the FQID: http://host/api/authors/uuid
            self.id = f"{self.host}authors/{self.uuid}"

        if not self.web:
            self.web = f"{self.host.replace("api/", "")}authors/{self.uuid}"
            
        super().save(*args, **kwargs)

class Entry(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.TextField()
    markdownContent = models.TextField(blank=True)

    github_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)
    url = models.URLField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.fqid:
            base_host = self.author.host if self.author.host.endswith('/') else f"{self.author.host}/"
            self.fqid = f"{base_host}authors/{self.author.uuid}/entries/{self.serial}"
            self.url = f"{base_host[:-4]}authors/{self.author.uuid}/entries/{self.serial}"
        if self.contentType == "text/markdown":
            self.markdownContent = markdown.markdown(self.content)
        return super().save(*args, **kwargs)

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    published = models.DateTimeField(default=timezone.now)
    contentType = models.CharField(max_length=200)
    comment = models.TextField()

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"{settings.BACKEND_URL}/api/authors/{self.author.uuid}/commented/{self.serial}"
        return super().save(*args, **kwargs)

class Like(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    #Like needs to work on an entry or a comment, so we need to use URL
    object_url = models.URLField(max_length=555)
    published = models.DateTimeField(default=timezone.now)

    serial = models.UUIDField(default=uuid.uuid4)
    fqid = models.URLField(blank=True, unique=True)

    class Meta:
        """dont let the author like the same thing more than once"""
        constraints = [
            models.UniqueConstraint(
                fields=["author", "object_url"],
                name="unique_like_per_author"
            )
        ]   
    def save(self, *args, **kwargs):
        if not self.fqid:
            self.fqid = f"{settings.BACKEND_URL}/api/authors/{self.author.uuid}/liked/{self.serial}"
        return super().save(*args, **kwargs)

class Follow(models.Model):
    
    
    #Alice follows Bob (bob accepts) and Bob follows Alice (accepted).
    #Separate friends model not required because we check for mutual
    #accepted follows
    
    # Track if a follow request is pending, accepted or declined
    #Each item is a tuple because the lowercase version is what gets stored
    #in the db and the capitalized version is what gets displayed in the admin
    #panel
    #for example, when we follow.status="declined" django stores "declined" in
    #the db but in the admin side of things, "Declined" is what would be shown
    
    #Django forms also only lets you pick from whats on the list. Cant type
    # a random value
    
    #Without choices, there could be potential risks of someone accidentally
    #storing "DECLINED", "deClInED", "Declined" or even "heck no" in the db
    #this limits us having to only choose what's defined
    
    #Source: https://docs.djangoproject.com/en/6.0/ref/models/fields/#choices
    #Date Accessed: Saturday, Feb. 28, 2026
    STATUS_CHOICES =[
        ('requesting', 'Requesting'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
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
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='requesting')
    
    # Optional: ensure an author can't follow the same person twice
    class Meta:
        unique_together = ('actor', 'object')
