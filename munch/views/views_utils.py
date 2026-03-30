from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *

from django.conf import settings

import requests as http_requests

def check_entry_visibility(request, entry):
    """
    Helper function that checks for entries visibility settings.
    - Created to be used in Comments and Likes API
    """
    if request.user.is_authenticated and request.user.is_superuser:
        return None
    
    if entry.visibility == "DELETED":
        return Response(status=status.HTTP_410_GONE)

    # Remote node authenticated via ServerBasicAuthentication
    # request.user is a Server instance, not an Author
    if isinstance(request.user, Server):
        if entry.visibility in ('PUBLIC', 'UNLISTED'):
            return None
        return Response(status=status.HTTP_403_FORBIDDEN)

    follows_author = Follow.objects.filter(
        actor=request.user,
        object=entry.author,
        status='accepted'
    ).exists()
    author_follows_user = Follow.objects.filter(
        actor=entry.author,
        object=request.user,
        status='accepted'
    ).exists()
    is_friend = follows_author and author_follows_user
    
    if entry.visibility == 'PRIVATE':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not is_friend and request.user != entry.author:
            return Response(status=status.HTTP_403_FORBIDDEN)

    elif entry.visibility == 'UNLISTED':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

def push_image_to_remote_followers(entry, author):
    """
    POST entry to inbox of all remote followers.
    """
    if not entry.contentType.startswith("image/"):
        return None
    
    remote_followers = Follow.objects.filter(
        object=author,
        status='accepted'
    ).select_related('actor').filter(
        actor__username__isnull=True 
    )
    
    entry_data = EntrySerializer(entry).data

    for follow in remote_followers:
        follower = follow.actor
        inbox_url = f"{follower.id.split('/authors/')[0]}/authors/{follower.id.split('/authors/')[1]}/inbox"
        
        if follower.id.split('/api/')[0] in settings.TRAILING_SLASH_HOSTS:
            inbox_url = f"{inbox_url}/"

        try:
            server = Server.objects.get(
                url__icontains=follower.host.replace('/api/', ''),
                is_approved=True
            )
        except Server.DoesNotExist:
            continue

        try:
            http_requests.post(
                inbox_url,
                json=entry_data,
                auth=(server.username, server.password),
                timeout=5
            )
        except http_requests.RequestException:
            continue