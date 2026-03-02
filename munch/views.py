from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AuthorUpdateForm, SignupForm, EntryForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.views import generic
from django.db.models import Q #without Q, Django gonna always filter to an "AND"
import markdown

import requests
from django.http import JsonResponse

from rest_framework import status
from django.conf import settings
from urllib.parse import quote
import re

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
    
    author = get_object_or_404(Author, uuid=author_uuid)
    entries = Entry.objects.filter(author=author)

    if request.user.is_authenticated and request.user == author:
        entries = entries.exclude(visibility='DELETED')
    else:
        visibility_filter = Q(visibility='PUBLIC')

        if request.user.is_authenticated:
            follows_author = Follow.objects.filter(
                actor=request.user,
                object=author,
                status='accepted'
            ).exists()
            author_follows_user = Follow.objects.filter(
                actor=author,
                object=request.user,
                status='accepted'
            ).exists()
            is_friend = follows_author and author_follows_user

            if follows_author:
                visibility_filter |= Q(visibility='UNLISTED')
            if is_friend:
                visibility_filter |= Q(visibility='PRIVATE')

        entries = entries.exclude(visibility='DELETED').filter(visibility_filter)
    
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
    
    If user is not approved by admin, log them out and send them back to login
    """
    if not request.user.is_approved:
        from django.contrib.auth import logout
        logout(request)
        from django.contrib import messages
        messages.error(request, "Account pending for approval by admin.")
        return redirect('munch:login')
    return redirect('munch:public_profile', author_uuid=request.user.uuid)

# The following function from Google, Gemini, "Django Login Function", 03-01-2026
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    from django.contrib import messages
    messages.info(request, "You have successfully logged out.")
    return redirect('munch:login')

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


def create_entry_UI(request, author_id):
    if not request.user.is_authenticated:
        return redirect('munch:login')

    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            return redirect('munch:display_entry_by_serial',
                            author_id=entry.author.uuid,
                            entry_serial=entry.serial)
    else:
        form = EntryForm()
        
    return render(request, 'munch/create_entry.html', {'form': form, 'title':"Create Entry", 'button_title':"Create Entry"})

def edit_entry(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    
    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            updated_entry = form.save(commit=False)
            updated_entry.author = entry.author
            updated_entry.save()
            return redirect(
                'munch:display_entry_by_serial',
                author_id=entry.author.uuid,
                entry_serial=entry.serial
            )
    else:
        form = EntryForm(instance=entry)

    return render(request, "munch/create_entry.html", {"form": form, "entry": entry, 'title':"Edit Entry", 'button_title':"Edit Entry"})

def delete_entry(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)

    if request.method == "POST":
        if request.user != entry.author:
            return redirect('munch:public_profile', author_uuid=author_id)

        entry.delete()
        return redirect('munch:public_profile', author_uuid=author_id)
    return redirect('munch:manage_entry_by_serial', author_id=author_id, entry_serial=entry_serial)

def display_entry_by_serial(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    author = get_object_or_404(Author, uuid=author_id)

    if request.user.is_authenticated:
        follows_author = Follow.objects.filter(
            actor=request.user,
            object=author,
            status='accepted'
        ).exists()
        author_follows_user = Follow.objects.filter(
            actor=author,
            object=request.user,
            status='accepted'
        ).exists()
        
        is_friend = follows_author and author_follows_user

        if entry.visibility == 'PRIVATE' and (not is_friend):
            return redirect('munch:public_profile', author_uuid=author_id)
        elif entry.visibility == 'DELETED':
            return redirect('munch:public_profile', author_uuid=author_id)
    else:
        if entry.visibility in ['PRIVATE', 'DELETED']:
            return redirect('munch:public_profile', author_uuid=author_id) # Get clarity on assumption of what "public" implies // Unauthenticated users to be considered?

    content = entry.content
    if entry.contentType == "text/markdown":
        content = markdown.markdown(entry.content)
    return render(request, "munch/entry_detail.html", {"entry": entry, "content":content})

def display_entry_by_FQID(request, entry_FQID):
    entry = get_object_or_404(Entry, fqid=entry_FQID)
    return render(request, "munch/entry_detail.html", {"entry": entry})

# # Following entry functions deal with the given API functions
@api_view(['GET', 'DELETE', 'PUT'])
def manage_entry_by_serial(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)

    if request.method == 'GET':

        # TODO - implement friend authentication if entry is friends only

        serializer = EntrySerializer(entry)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if not request.user.is_authenticated or request.user != entry.author:
            return Response(
                {"detail": "Only the author can update this entry."},
                status=status.HTTP_403_FORBIDDEN
            )

        entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
        serializer = EntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save(author=entry.author)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated or request.user != entry.author:
            return Response(
                {"detail": "Only the author can update this entry."},
                status=status.HTTP_403_FORBIDDEN
            )
        entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def manage_entry_by_FQID(request, entry_FQID):
    entry = get_object_or_404(Entry, fqid=entry_FQID)

    # TODO - implement friend authentication if entry is friends only
    
    serializer = EntrySerializer(entry)
    return Response(serializer.data)

@api_view(['GET','POST'])
def create_entry(request, author_id):
    if request.method == "GET":
        # TODO - Not authenticated: only public entries.
        # TODO - Authenticated locally as author: all entries.
        # TODO - Authenticated locally as follower of author: public + unlisted entries.
        # TODO - Authenticated locally as friend of author: all entries.
        # TODO - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local entries is by local node pushing those entries to inbox, not by remote node pulling.

        # obtain the 5 most recent entries and return it
        entries = Entry.objects.filter(author__uuid=author_id).order_by('-published')[:5]
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":

        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_403_FORBIDDEN
            )

        if str(request.user.uuid) != str(author_id):
            return Response(
                {"detail": "Only the author can create entries here."},
                status=status.HTTP_403_FORBIDDEN
            )

        # TODO - implement ability to post images 

        serializer = EntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
        Q(visibility = 'PRIVATE', author__in=user_friends) |
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
@login_required
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

@api_view(['GET'])
def get_authors(request):
    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_authors_paginated(request):
    page = request.GET.get('page')
    size = request.GET.get('size')

    if (page != None) and (size != None):
        start = page * size
        end = start + size

        authors = Author.objects.all()[start:end]
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    elif (page == None) and (size == None):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def get_author(request, author_id):
    id_type = 'FQID' if (author_id.find("http://") != -1) else 'serial'

    if id_type == 'serial':
        fqid = f"{settings.BACKEND_URL}/munch/api/authors/{author_id}"
    else:
        fqid = author_id
    
    author = Author.objects.get(id=fqid)
    if author == None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    
    elif request.method == 'PUT' and id_type == 'serial':
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Following API

@login_required
@api_view(['GET'])
def get_following(request, author_serial):
    author = Author.objects.get(uuid=author_serial)

    # get authors that are in a follower_relations relation with the specified actor
    following = Author.objects.filter(follower_relations__actor=author)

    serializer = AuthorSerializer(following, many=True)
    return Response(serializer.data)
    
@login_required
@api_view(['GET', 'DELETE', 'PUT'])
def manage_following(request, author_serial, target_FQID):
    follow_entry = Follow.objects.filter(actor__uuid=author_serial, object__id=target_FQID).first()

    if request.method == 'GET':
        follow_entry = Follow.objects.filter(actor__uuid=author_serial, object__id=target_FQID, status='accepted').first()
        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        follow_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':

        # to be used for future milestones maybe
        # capture group 1: 0+ chars as few as possible until 
        # capture group 2: 1+ chars until /
        regex_match = re.search(r'^(.*?api\/authors\/)([^/]+)', target_FQID)
        target_service = regex_match.group(1)
        target_serial = regex_match.group(2)

        # create follow object if none exists yet
        if follow_entry == None:

            target_author = Author.objects.get(id=target_FQID)
            if target_author == None:
                # TODO request user data from other nodes in future milestones
                return Response(status=status.HTTP_400_BAD_REQUEST)
            actor_author = Author.objects.get(id=f"{settings.BACKEND_URL}/munch/api/authors/{author_serial}")

            follow_entry = Follow(
                actor=actor_author,
                object=target_author,
                status='requesting'
            )
        
        # serialize follow request and post to target inbox
        serializer = FollowRequestSerializer(follow_entry)
        response = requests.post(f"{target_service}{target_serial}/inbox", json=serializer.data)

        if response.status_code == 201:
            return Response(response.json())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# Followers API

@api_view(['GET', 'DELETE', 'PUT'])
def manage_follower(request, author_serial, target_FQID):
    
    if request.method == 'GET':
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial, status='accepted').first()

        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)
    
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Authentication is required'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if request.method == 'DELETE':
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial).first()
        if follow_entry != None:
            follow_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial).first()

        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        follow_entry.status = 'accepted'
        follow_entry.save()

        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)

# Follow Request API

@api_view(['GET'])
def get_follow_requests(request, author_serial):
    author = Author.objects.get(id=f"{settings.BACKEND_URL}/munch/api/authors/{author_serial}")

    # get authors that are requesting to follow given author
    follow_requests = Author.objects.filter(following_relations__object=author, following_relations__status='requesting')

    serializer = AuthorSerializer(follow_requests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def follow(request, target_serial):
    serializer = FollowRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=400, data=serializer.errors)

# Entries API

# Image Entries API

# Comments API

# Commented API

# Likes API

# Liked API
