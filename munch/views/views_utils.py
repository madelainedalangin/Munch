from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *

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