from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AuthorUpdateForm, SignupForm, EntryForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.views import generic
from django.db.models import Q #without Q, Django gonna always filter to an "AND"

import requests
from django.http import JsonResponse

host = 'http://127.0.0.1/'

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = AuthorUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect back to their public profile after saving
            return redirect('munch:public_profile', author_uuid=request.user.uuid)
    else:
        form = AuthorUpdateForm(instance=request.user)
    
    return render(request, 'munch/edit_profile.html', {'form': form})

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
def public_profile(request, author_uuid):
    # This matches the <uuid:author_uuid> in your urls.py
    author = get_object_or_404(Author, uuid=author_uuid)
    entries = Entry.objects.filter(author__uuid=author_uuid)
    
    # For now, only pass the author. 
    # add 'posts' for user story 5 when implemented
    context = {
        'author': author,
        'entries': entries,
    }
    return render(request, 'munch/public_profile.html', context)

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
@login_required
def login_success_redirect(request):
    """
    Redirects the user to their specific public profile after login.
    """
    return redirect('munch:public_profile', author_uuid=request.user.uuid)

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('munch:login') # Send to login after signup
    else:
        form = SignupForm()
    return render(request, 'munch/signup.html', {'form': form})

class FollowersView(generic.TemplateView):
    template_name = "munch/followers.html"

def createEntry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            return redirect(entry.fqid)
    else:
        form = EntryForm()
        
    return render(request, 'munch/create_post.html', {'form': form})

def manage_entry_by_serial(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    return render(request, "munch/entry_detail.html", {"entry": entry})


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
    
    #Gimme a list of author IDs the user currently logged in is following
    user_follows = Follow.objects.filter(actor=user, status='accepted')
    
    #Gimme a list of author IDs the user currently logged in is following
    # but not the full follow object
    user_following = user_follows.values_list('object', flat=True)
    
    #Source: https://docs.djangoproject.com/en/6.0/ref/models/querysets/#top
    #Date Accessed: Feb. 28, 2026
    
    user_friends = Follow.objects.filter(
        actor__in = user_following,
        object = user,
        status = 'accepted'
    ).values_list('actor', flat=True)
    
    #Source: https://www.freecodecamp.org/news/what-is-q-in-django-and-why-its-super-useful/
    #Date Accessed: Saturday, Feb. 28, 2026
    #This answers the question of, what posts/entries should a user currently
    #logged in should see?
    entries = Entry.objects.filter(
        Q(visibility = 'PUBLIC') | 
        Q(visibility = 'UNLISTED', author__in=user_following) |
        Q(visibility = 'FRIENDS', author__in=user_friends) |
        Q(author = user)
    ).exclude(
        visibility = 'DELETED'
    ).order_by('-published')
    
    return entries

@login_required
def stream(request):
    """
    Purpose: This function is UI for the stream page.
    
    Args:
        request: HTTP GET req from user

    Returns:
        Rendered HTML page displaying what the user's stream
    """
    entries = get_stream_entries(request.user)
    return render(request, 'munch/stream.html', {'entries': entries})
      
@api_view(['GET'])
def stream_api(request):
    """
    Purpose: This function runs whenever some user peeps /munch/stream
    Args:
        request: HTTP GET req from user

    Returns:
        Response: JSON list of entry obj user should be seeing in their 
        homepage.
    """
    entries = get_stream_entries(request.user)
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
    return Response(entries_list)

# Authors API

# Following API

@api_view(['GET'])
def get_following(request, author_serial):
    author = Author.objects.get(uuid=author_serial)

    # get authors that are in a follower_relations relation with the specified actor
    following = Author.objects.filter(follower_relations__actor=author)

    serializer = AuthorSerializer(following, many=True)
    return Response(serializer.data)
    

@api_view(['GET', 'DELETE', 'PUT'])
def manage_following(request, author_serial, target_FQID):
    follow_entry = Follow.objects.filter(actor__uuid=author_serial, object__id=target_FQID).first()

    if request.method == 'GET':
        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if follow_entry == None:
            return
        
        follow_entry.delete()

    elif request.method == 'PUT':
        if follow_entry == None:
            return
        
        url = target_FQID
        if url.find("api/authors/") == -1:
            url = f"{url.replace("/authors/", "api/authors/")}/inbox"
        
        serializer = FollowRequestSerializer(follow_entry)
        response = requests.post(url, json=serializer.data)
        return JsonResponse(response.json)


# Followers API

@api_view(['GET', 'DELETE', 'PUT'])
def manage_follower(request, author_serial, target_FQID):
    
    
    if request.method == 'GET':
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial, status='accepted').first()
        

    elif request.method == 'DELETE':
        pass

    elif request.method == 'PUT':
        pass

# Follow Request API

@api_view(['GET'])
def get_follow_requests(request, author_serial):
    author = Author.objects.get(id=f"{host}/api/authors/{author_serial}")

    # get authors that are requesting to follow given author
    follow_requests = Author.objects.filter(following_relations__object=author, following_relations__status='requesting')

    serializer = AuthorSerializer(follow_requests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def follow(request, author_serial):
    serializer = FollowRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(status=400, data=serializer.errors)

# Entries API

# Image Entries API

# Comments API

# Commented API

# Likes API

# Liked API
