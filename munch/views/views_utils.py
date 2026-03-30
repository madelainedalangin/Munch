from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *
import requests as http_requests

#-helper function for entry visibility
def check_entry_visibility(request, entry):
    """
    Helper function that checks for entries visibility settings.
    - Created to be used in Comments and Likes API
    """
    if request.user.is_authenticated and request.user.is_superuser:
        return None
    
    if entry.visibility == "DELETED":
        return Response(status=status.HTTP_410_GONE)
    
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
        # Extract base host from follower's FQID
        # e.g. http://remotenode.com/api/authors/1111 -> http://remotenode.com/api/
        inbox_url = f"{follower.id.split('/authors/')[0]}/authors/{follower.id.split('/authors/')[1]}/inbox/"

        # Find a Server credential for this remote node
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
            continue  # no crashing :') PLEASEEEE