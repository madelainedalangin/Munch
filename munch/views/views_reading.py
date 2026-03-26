from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q #without Q, Django gonna always filter to an "AND"

from rest_framework.decorators import api_view
from rest_framework.response import Response

from munch.serializers import *
from munch.models import *

# The following function from Google, Gemini, "Django Shareable Link", 03-15-26
@login_required
def public_browse(request):
    """The new Global Discovery stream"""
    # Fetch all PUBLIC entries from everyone
    entries = Entry.objects.filter(visibility='PUBLIC').exclude(visibility='DELETED').order_by('-published')
    return render(request, 'munch/stream.html', {
        'entries': entries,
        'global_view': True  
    })

def get_stream_entries(user):
    """
    Purpose: Helper function for stream and stream_api. Avoids code smell
    
    This function finds which people the user follows,
    user's friends and gets public entries from anyone, unlisted from
    the people they follow, friends from friends and user's own entries.
    It removes deleted entries and sorts the entries newest first
    
    Arguments: author/user object of whoever is currently logged in
    Return: a QuerySet of entry objects
    """

    # Superuser bypass to view all public and deleted entries
    if user.is_superuser:
        entries = Entry.objects.filter(
            Q(visibility = 'PUBLIC') | 
            Q(visibility = 'DELETED') |
            Q(visibility = 'UNLISTED') |
            Q(author = user)
        ).order_by('-published')
        
        return entries
    
    #Gimme a list of author IDs the user currently logged in is following
    user_follows = Follow.objects.filter(actor=user, status='accepted')
    
    #Gimme a list of author IDs the user currently logged in is following
    # but not the full follow object
    user_following = user_follows.values_list('object__id', flat=True)
    
    #Source: https://docs.djangoproject.com/en/6.0/ref/models/querysets/#top
    #Date Accessed: Feb. 28, 2026
    
    user_friends = Follow.objects.filter(
        actor__in = user_following,
        object = user,
        status = 'accepted'
    ).values_list('actor__id', flat=True)
    
    #Source: https://www.freecodecamp.org/news/what-is-q-in-django-and-why-its-super-useful/
    #Date Accessed: Saturday, Feb. 28, 2026
    #This answers the question of, what posts/entries should a user currently
    #logged in should see?
    entries = Entry.objects.filter(
        Q(visibility='PUBLIC') | 
        Q(author__in=user_following, visibility='UNLISTED') |
        Q(author__in=user_friends, visibility='PRIVATE') |
        Q(author = user)
    ).exclude(
        visibility = 'DELETED'
    ).order_by('-published')
    
    return entries

@login_required
def stream(request):
    entries = get_stream_entries(request.user)
    
    # Sourced from get_stream_entries function
    # Only show entries of users followed
    user_following_ids = Follow.objects.filter(
        actor=request.user, 
        status='accepted'
    ).values_list('object', flat=True)
    entries = entries.filter(
        Q(author__in=user_following_ids) | Q(author=request.user)
    )
    
    page = int(request.GET.get('page', 1))
    size = 10
    start = (page - 1) * size
    end = start + size
    total = entries.count()
    total_pages = max(1, (total + size - 1) // size)
    entries = entries[start:end]
    
    return render(request, 'munch/stream.html', {
        'entries': entries,
        'page': page,
        'total_pages': total_pages,
        'total': total,
    })
      
@api_view(['GET'])
@login_required
def stream_api(request):
    """
    Purpose: This function runs whenever some user peeps /stream
    Args:
        request: HTTP GET req from user

    Returns:
        Response: JSON list of entry obj user should be seeing in their 
        homepage.
    """
    entries = get_stream_entries(request.user)
    #pagination
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    start = (page - 1) * size
    end = start + size
    total = entries.count()
    entries = entries[start:end] 
    entries_list = []
    
    for entry in entries:
        entries_list.append({
            "type": "entry",
            "title": entry.title,
            "id": entry.fqid,
            "description": entry.description,
            "contentType": entry.contentType,
            "content": entry.content,
            "author": {
                "type": "author",
                "id": entry.author.id,
                "host": entry.author.host,
                "displayName": entry.author.displayName,
                "github": entry.author.github,
                "profileImage": entry.author.profileImage,
            },
            "published": entry.published.isoformat(),
            "visibility": entry.visibility,
        })
    return Response({
                    "type": "entries",
                    "page_number": page,
                    "size": size,
                    "count": total,
                    "src": entries_list
                    })