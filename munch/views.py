from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AuthorUpdateForm
from .models import Author, Follow, Entry
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,EntryForm

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from .models import *
from django.views import generic
from django.db.models import Q #without Q, Django gonna always filter to an "AND"

import requests
from django.http import JsonResponse

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
@login_required
def stream(request):
    
    #Gimme a list of author IDs the user currently logged in is following
    user_follows = Follow.objects.filter(actor=request.user, status='accepted')
    
    #Gimme a list of author IDs the user currently logged in is following
    # but not the full follow object
    user_following = user_follows.values_list('object', flat=True)
    
    #Source: https://docs.djangoproject.com/en/6.0/ref/models/querysets/#top
    #Date Accessed: Feb. 28, 2026
    
    user_friends = Follow.objects.filter(
        actor__in = user_following,
        object = request.user,
        status = 'accepted'
    ).values_list('actor', flat=True)
    
    #Source: https://www.freecodecamp.org/news/what-is-q-in-django-and-why-its-super-useful/
    #Date Accessed: Saturday, Feb. 28, 2026
    #This answers the question of, what posts/entries should a user currently
    #logged in should see?
    entries = Entry.objects.filter(
        #Get all public posts on the node OR
        #Get unlisted posts from the authors user follows (ONLY) OR
        #Get posts only from friends OR
        #Get user's own posts
        #Exclude deleted entries even user's own entries
        #order it by newest first (not like those twitter algorithms now T^T)
        Q(visibility = 'PUBLIC') | 
        Q(visibility = 'UNLISTED', author__in=user_following) |
        Q(visibility = 'FRIENDS', author__in=user_friends) |
        Q(author = request.user)
    ).exclude(
        visibility = 'DELETED'
    ).order_by('-published')
    context = {
        'entries': entries,
    }
    return render(request, 'munch/stream.html', context)


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
        serializer = FollowSerializer(follow_entry)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if follow_entry == None:
            return
        
        follow_entry.delete()

    elif request.method == 'PUT':
        if follow_entry == None:
            return
        
        url = f"{target_FQID.replace("/authors/", "api/authors/")}/inbox"
        serializer = FollowRequestSerializer(follow_entry)
        response = requests.post(url, json=serializer.data)
        return JsonResponse(response.json)


# Followers API

# Follow Request API

# Entries API

# Image Entries API

# Comments API

# Commented API

# Likes API

# Liked API
