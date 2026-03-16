from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import AuthorUpdateForm, SignupForm, EntryForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.conf import settings
from django.views import generic
from django.db.models import Q #without Q, Django gonna always filter to an "AND"
import markdown

import requests
from django.http import JsonResponse

from rest_framework import status
from urllib.parse import quote
import re

from .utils import sync_github_activity
from django.db import IntegrityError #for liked function
import base64 #for image_entry api

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

    try:
        sync_github_activity(author)
    except Exception as e:
        # We wrap this in try/except so if GitHub is down, 
        # the profile page still loads.
        print(f"GitHub sync failed: {e}")

    entries = Entry.objects.filter(author=author)

    if request.user.is_authenticated and request.user.is_superuser:
        entries = entries.order_by("-published")
    elif request.user.is_authenticated and request.user == author:
        entries = entries.exclude(visibility='DELETED').order_by("-published")
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

    entries = entries.order_by('-published')
    
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
    Redirects the user to the stream after login.
    
    If user is not approved by admin, log them out and send them back to login
    """
    if not request.user.is_approved:
        from django.contrib.auth import logout
        logout(request)
        from django.contrib import messages
        messages.error(request, "Account pending for approval by admin.")
        return redirect('munch:login')
    return redirect('munch:stream')

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

def followers_view(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)   # use fqid in future
    follower_list = Author.objects.filter(following_relations__object=author)
    context = {
        "user": author,
        "followers": follower_list
    }
    return render(request, 'munch/followers.html', context)

def list_following(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)
    following_list = Author.objects.filter(follower_relations__actor=author)
    context = {
        "user": author,
        "following": following_list
    }
    return render(request, 'munch/following_list.html', context)

def list_follow_requests(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)
    follower_list = Author.objects.filter(following_relations__object=author, following_relations__status='requesting')
    context = {
        "user": author,
        "followers": follower_list
    }
    return render(request, 'munch/follow_request_list.html', context)

def create_entry_UI(request, author_id):
    '''
    Purpose: Creates an entry through a filled out form from the user in the UI 

    If user fills the form correctly, it will save as an entry in the database
    '''
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
    '''
    Purpose: Modifies an existing form created by the author in the UI

    User will be taken to a page with the entry details already filled in which they can modify and save once they are done
    '''
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    
    if request.method == "POST":
        form = EntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            updated_entry = form.save(commit=False)
            updated_entry.author = entry.author
            
            image_file = request.FILES.get("image")
            if image_file:
                # new image uploaded
                image_data = image_file.read()
                updated_entry.content = base64.b64encode(image_data).decode("utf-8")
                updated_entry.contentType = image_file.content_type + ';base64'
            elif entry.contentType.startswith('image/'):
                # no new image uploaded — restore original content from database
                updated_entry.content = entry.content
                updated_entry.contentType = entry.contentType
            
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
    '''
    Purpose: Deletes an author's entry
    '''
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)

    if request.method == "POST":
        if request.user != entry.author:
            return redirect('munch:public_profile', author_uuid=author_id)

        entry.visibility = "DELETED"
        entry.save()
        return redirect('munch:public_profile', author_uuid=author_id)
    return redirect('munch:manage_entry_by_serial', author_id=author_id, entry_serial=entry_serial)

@login_required
def display_entry_by_serial(request, author_id, entry_serial):
    '''
    Purpose: Display a given entry's details 

    If you are the author of the entry, you will have access to modify and delete it through the UI
    '''
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    author = get_object_or_404(Author, uuid=author_id)
    
    comments = Comment.objects.filter(entry=entry).order_by("-published")

    #superuser bypass
    if request.user.is_superuser:
            return render(
                request, 
                "munch/entry_detail.html", 
                {
                    "entry": entry, 
                    "comments": comments
                })

    if request.user == author:
        if entry.visibility == 'DELETED':
            return HttpResponse(status=410)
        return render(request, "munch/entry_detail.html", {"entry": entry, "comments": comments})

    # If a user is logged in and has the link to a PUBLIC or UNLISTED post, let them see it.
    if entry.visibility in ['PUBLIC', 'UNLISTED']:
        return render(request, "munch/entry_detail.html", {"entry": entry, "comments": comments})

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

    if entry.visibility == 'DELETED':
        return HttpResponse(status=410)
    elif entry.visibility == 'PRIVATE' and (not is_friend):
        return HttpResponse(status=403)

    return render(request, "munch/entry_detail.html", {"entry": entry, "comments": comments})

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

# (this function may be used in the future)
# def display_entry_by_FQID(request, entry_FQID):
#     entry = get_object_or_404(Entry, fqid=entry_FQID)
#     return render(request, "munch/entry_detail.html", {"entry": entry})

# # Following entry functions deal with the given API functions
@api_view(['GET', 'DELETE', 'PUT'])
def manage_entry_by_serial(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)

    if request.method == 'GET':
        visibility_error = check_entry_visibility(request, entry)
        if visibility_error:
            return visibility_error
        
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
        
        if entry.visibility == "DELETED":
            return Response({"detail": "Entry already deleted."},status=status.HTTP_204_NO_CONTENT)
        entry.visibility = "DELETED"
        entry.save()
        
        return Response({"detail": "Entry successfully deleted."},status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def manage_entry_by_FQID(request, entry_FQID):
    entry = get_object_or_404(Entry, fqid=entry_FQID)

    # TODO - implement friend authentication if entry is friends only
    
    serializer = EntrySerializer(entry)
    return Response(serializer.data)

@api_view(['GET','POST'])
def create_entry(request, author_id):
    """
    GET api/authors/{AUTHOR_SERIAL}/entries/
    """
    
    if request.method == "GET":
        author = get_object_or_404(Author, uuid=author_id)
        entries = Entry.objects.filter(
            author=author
            ).exclude(
                visibility="DELETED"
                ).order_by(
                    "-published"
                    )
        #only public entries can be seen if they are unauthenticated users
        if not request.user.is_authenticated:
            entries = entries.filter(visibility="PUBLIC")
            
        elif request.user != author:
            follows_author = Follow.objects.filter(
                actor=request.user, 
                object=author,
                status="accepted",
                ).exists()
            
            author_follows_user = Follow.objects.filter(
                actor=author,
                object=request.user,
                status="accepted",
            ).exists()
            
            both_friends = follows_author and author_follows_user
            
            if not both_friends:
                if follows_author:
                    #entries in public and unlisted setting can be seen by followers
                    entries = entries.filter(visibility__in=["PUBLIC", "UNLISTED"])
                else:
                    #strangers can only see public
                    entries = entries.filter(visibility="PUBLIC")

        
        #also include pagination
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))
        start = (page - 1) * size
        end = start + size
        total = entries.count()
        entries = entries[start:end]
        serializer = EntrySerializer(entries, many=True)
        
        return Response({
                        "type": "entries",
                        "page_number": page,
                        "size": size,
                        "count": total,
                        "src": serializer.data
                        })
    
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

@login_required
def settings_page(request): #renamed to settings_page its overwriting our import settings from django
    return render(request, 'munch/settings.html')

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
@api_view(['GET'])
def get_image_by_serial(request, author_serial, entry_serial):
    #Entry model contentType is plain CharField
    #lookup entry by serial
    #check if contentType starts with image/ if not return 404
    #decode base64 content field
    #return HTTPResponse with content type
    entry = get_object_or_404(Entry, author__uuid=author_serial, serial=entry_serial)
    if not entry.contentType.startswith("image/"):
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #people shouldnt be able to access the private image entries without
    #any permission
    visibility_error = check_entry_visibility(request, entry)
    if visibility_error:
        return visibility_error
    
    #Source: https://docs.python.org/3/library/base64.html
    #Date Accessed: Saturday, March 14, 2026
    #entry.content is an ASCII str, and it returns the decoded
    #i require to decode entry.content using base64.b64decode()
    #also mentioned in the project spec
    image_data = base64.b64decode(entry.content)
    
    #before split: reinhardt_image/png;base64
    #after split: reinhardt_image/png
    entry_content_type = entry.contentType.split(";")[0]
    return HttpResponse(image_data, content_type=entry_content_type)

@api_view(['GET'])
def get_image_by_fqid(request, entry_fqid):
    """similar to serial version except we are using entry fqid"""
    #Entry model contentType is plain CharField
    #lookup entry by serial
    #check if contentType starts with image/ if not return 404
    #decode base64 content field
    #return HTTPResponse with content type
    entry = get_object_or_404(Entry, fqid=entry_fqid)
    if not entry.contentType.startswith("image/"):
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #people shouldnt be able to access the private image entries without
    #any permission
    visibility_error = check_entry_visibility(request, entry)
    if visibility_error:
        return visibility_error
    
    #Source: https://docs.python.org/3/library/base64.html
    #Date Accessed: Saturday, March 14, 2026
    #entry.content is an ASCII str, and it returns the decoded
    #i require to decode entry.content using base64.b64decode()
    #also mentioned in the project spec
    image_data = base64.b64decode(entry.content)
    
    #before split: reinhardt_image/png;base64
    #after split: reinhardt_image/png
    entry_content_type = entry.contentType.split(";")[0]
    return HttpResponse(image_data, content_type=entry_content_type)

@login_required
def create_entry_UI(request, author_id):
    '''
    Purpose: Creates an entry through a filled out form from the user in the UI 

    If user fills the form correctly, it will save as an entry in the database
    '''
    if not request.user.is_authenticated:
        return redirect('munch:login')

    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES) 
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            
            image_file = request.FILES.get('image')
            if image_file:
                image_data = image_file.read()
                entry.content = base64.b64encode(image_data).decode('utf-8')
                entry.contentType = image_file.content_type + ';base64'
            
            entry.save()
            return redirect('munch:display_entry_by_serial',
                            author_id=entry.author.uuid,
                            entry_serial=entry.serial)
    else:
        form = EntryForm()
        
    return render(
        request, 
        'munch/create_entry.html', 
        {
            'form': form, 
            'title':"Create Entry", 
            'button_title':"Create Entry"
        })

# Likes API

@api_view(["GET"])
def get_entry_likes(request, author_serial, entry_serial):
    """
    GET api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/likes/

    This function gets a paginated list of all da likes on a specific entry
    ensuring the visibility settings are not tampered with.
    
    - private entries are only accesible to friends.
    - unlisted to followers
    - deleted entries return 410.
    
    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the entry's author
        entry_serial: UUID of the entry being queried

    Returns:
        Response: A paginated likes object containing type, web, id, 
            page_number, size, count, and src (list of like objects).
            Returns 403 (unauthorized), 410 (deleted entry)).
    """
    
    entry = get_object_or_404(
        Entry, 
        author__uuid=author_serial, 
        serial=entry_serial
        )
    visibility_error = check_entry_visibility(request, entry)
    
    if visibility_error:
        return visibility_error
    
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(author__uuid=request.user.uuid,object_url=entry.fqid).exists()

    entry_likes = Like.objects.filter(object_url=entry.fqid)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_entry_likes = entry_likes.count()
    entry_likes = entry_likes[start_page:end_page]
    serializer = LikeSerializer(entry_likes, many=True)
    
    return Response({
        "type": "likes",
        "web": f"{settings.BACKEND_URL}/authors/{author_serial}/entries/{entry_serial}/",
        "id": f"{settings.BACKEND_URL}/api/authors/{author_serial}/entries/{entry_serial}/likes/",
        "page_number": page,
        "size": size,
        "count": total_entry_likes,
        "src": serializer.data,
        "user_liked": user_liked,
        })

@api_view(["GET"])
def get_entry_likes_by_fqid(request, entry_fqid):
    # Source: https://stackoverflow.com/questions/71771838/python-urllib-url-quote-unquote-issue
    # Date Accessed: March 15, 2026

    #fqid is percent enncoded URL
    #unquote converts it back to http
    #without it, django gonna look for an entry with a %-encoded url and that doesnt
    #match anything in our db
    from urllib.parse import unquote
    entry_fqid = unquote(entry_fqid)
    
    entry = get_object_or_404(Entry, fqid=entry_fqid)
    
    visibility_error = check_entry_visibility(request, entry)
    
    if visibility_error:
        return visibility_error
    
    entry_likes = Like.objects.filter(object_url=entry.fqid)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_entry_likes = entry_likes.count()
    entry_likes = entry_likes[start_page:end_page]
    serializer = LikesSerializer(entry_likes, many=True)
    
    return Response({
        "type": "likes",
        "web": f"{settings.BACKEND_URL}/authors/{entry.author.uuid}/entries/{entry.serial}/",
        "id": f"{entry_fqid}/likes/",
        "page_number": page,
        "size": size,
        "count": total_entry_likes,
        "src": serializer.data,
        })

@api_view(["GET"])
def get_comment_likes(request, author_serial, entry_serial, comment_serial):
    """
    GET api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{COMMENT_SERIAL}/likes/
    This function gets likes on a specific comment. The likes is a list and is
    paginated.
    
    Visibility based on the parent entry's visibility settings.
    
    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the comment's author
        entry_serial: UUID of the parent entry
        comment_serial: UUID of the comment being queried

    Returns: 
        Response: A paginated likes object containing type, web, id,
        page_number, size, count, and src (list of like objects).
        
        - Returns 403 if unauthorized, 410 if parent entry is deleted.
    """
    
    entry = get_object_or_404(Entry, serial=entry_serial)
    comment = get_object_or_404(
        Comment,
        entry=entry,
        author__uuid=author_serial,
        serial=comment_serial
    )
    visibility_error = check_entry_visibility(request, comment.entry)
    
    if visibility_error:
        return visibility_error
    
    comment_likes = Like.objects.filter(object_url=comment.fqid)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_comment_likes = comment_likes.count()
    comment_likes = comment_likes[start_page:end_page]
    serializer = LikeSerializer(comment_likes, many=True)
    
    author_str = f"authors/{author_serial}"
    entries_str = f"entries/{entry_serial}"
    comments_str = f"comments/{comment_serial}"
    
    return Response({
        "type": "likes",
        "web": f"{settings.BACKEND_URL}/{author_str}/{entries_str}/{comments_str}/",
        "id": f"{settings.BACKEND_URL}/api/authors/{author_str}/{entries_str}/{comments_str}/likes/",
        "page_number": page,
        "size": size,
        "count": total_comment_likes,
        "src": serializer.data,
        })

@api_view(["GET"])
def get_like_by_serial(request, author_serial, like_serial):
    """
    This function gets a single like by the author's serial and like's serial.

    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the like's author
        like_serial: UUID of the like being queried

    Returns:
        Response: A single like object. Returns 404 if not found.
    """
    like = get_object_or_404(Like, author__uuid=author_serial, serial=like_serial)
    serializer = LikeSerializer(like)
    return Response(serializer.data)

@api_view(["GET"])
def get_like_by_fqid(request, like_fqid):
    """
    This function gets a single like by its FQID (whether entry or comment).
    It also has visibility checks of the liked entry or comment.

    Args:
        request: HTTP GET request from the client
        like_fqid: Full URL identifier of the like

    Returns:
        Response: A single like object. Returns 403 if unauthorized,
                410 if the liked entry is deleted, 404 if not found.
    """
    like = get_object_or_404(Like, fqid=like_fqid)
    
    if "entries" in like.object_url:
        entry = get_object_or_404(Entry, fqid=like.object_url)
        visibility_error = check_entry_visibility(request, entry)
    else:
        comment = get_object_or_404(Comment, fqid=like.object_url)
        visibility_error = check_entry_visibility(request, comment.entry)
    if visibility_error:
        return visibility_error
    
    serializer = LikeSerializer(like)
    return Response(serializer.data)

# Liked API
@api_view(["GET", "POST", "DELETE"])
def liked(request, author_serial):
    """
    This function handles entries and comments that have been liked.
    
    GET: Returns a paginated list of all likes made by a specific author.
    POST: Creates a new like by the author on an entry or comment.
    Accepts both serial and FQID to identify author.

    Args:
        request: HTTP GET or POST request from the client
        author_serial: UUID or FQID of the author

    Returns:
        GET - Response: paginated likes object containing type, id,
                        page_number, size, count, and src (list of like objects).
        POST - Response: the created like object with status 201.
                        Returns 400 if object field is missing or already liked.
                        Returns 404 if author not found.
        *DELETE - Response: delete the like object with status 204.
                        Return 404 if like object not found
    """
    
    id_type = "FQID" if (author_serial.find("http://") != -1) else "serial"
    if id_type == "serial":
        author = get_object_or_404(Author, uuid=author_serial)
    else:
        author = get_object_or_404(Author, id=author_serial)
    
    if request.method == "GET":
        author_likes = Like.objects.filter(author=author)
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))
        start_page = (page - 1) * size
        end_page = start_page + size
        total_author_likes = author_likes.count()
        author_likes = author_likes[start_page:end_page]
        serializer = LikeSerializer(author_likes, many=True)
        return Response({
            "type": "likes",
            "id": f"{settings.BACKEND_URL}/api/authors/{author_serial}/liked/",
            "page_number": page,
            "size": size,
            "count": total_author_likes,
            "src": serializer.data,
        })
    elif request.method == "POST":
        object_url = request.data.get("object")
        if not object_url:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            like = Like.objects.create(author=author, object_url=object_url)
        except IntegrityError:
            return Response({"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LikeSerializer(like)
        try:
            if "entries" in object_url:
                entry = Entry.objects.filter(fqid=object_url).first()
                if entry:
                    inbox_url = f"{entry.author.host}authors/{entry.author.uuid}/inbox"
                    requests.post(inbox_url, json=serializer.data)
            else:
                comment = Comment.objects.filter(fqid=object_url).first()
                if comment:
                    inbox_url = f"{comment.author.host}authors/{comment.author.uuid}/inbox"
                    requests.post(inbox_url, json=serializer.data)
        except Exception as e:
            print(f"Failed to forward like notification to inbox: {e}")
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # DELETE request was added on top of user stories for better user experience
    elif request.method == "DELETE":
        object_url = request.data.get("object")
        like = get_object_or_404(Like, author=author, object_url=object_url)
        like.delete()
        return Response({"detail": "Like successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

# Comments API

@api_view(["GET"])
def get_comment_by_serial(request, author_serial, comment_serial):
    """
    This function gets a comment by the author's serial and comment's serial.
    Visibility is checked against the comment's parent entry.

    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the comment's author
        comment_serial: UUID of the comment being queried

    Returns:
        Response: A single comment object. Returns 403 if unauthorized,
                410 if parent entry is deleted, 404 if not found.
    """

    comment = get_object_or_404(Comment, author__uuid=author_serial, serial=comment_serial)
    visibility_error = check_entry_visibility(request, comment.entry)
    if visibility_error:
        return visibility_error
    serializer = CommentSerializer(comment)
    return Response(serializer.data)

@api_view(["GET"])
def get_comment_by_fqid(request, comment_fqid):
    """
    This function gets a single comment using its fqid

    Args:
        request: HTTP GET request from the client
        comment_fqid: FQID of the comment

    Returns:
        Response: a single comment obj. Returns 403 if unauthorized,
        410 if parent entry is deleted, 404 if not found.
    """
    
    comment = get_object_or_404(Comment, fqid=comment_fqid)
    visibility_error = check_entry_visibility(request, comment.entry)
    if visibility_error:
        return visibility_error
    serializer = CommentSerializer(comment)
    return Response(serializer.data)
    
@api_view(["GET"])
def get_entry_comments_by_serial(request, author_serial, entry_serial):
    """
    This function is getting comments from an entry using the entry's serial 
    and the author's serial
    """
    
    entry = get_object_or_404(
        Entry, 
        author__uuid=author_serial, 
        serial=entry_serial
        )
    visibility_error = check_entry_visibility(request, entry)
    
    if visibility_error:
        return visibility_error
    
    entry_comments = Comment.objects.filter(entry=entry)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start = (page - 1) * size
    end = start + size
    total_entry_comments = entry_comments.count()
    entry_comments = entry_comments[start:end]
    serializer = CommentSerializer(entry_comments, many=True)
    return Response({
        "type": "comments",
        "web": f"{settings.BACKEND_URL}/authors/{author_serial}/entries/{entry_serial}/",
        "id": f"{settings.BACKEND_URL}/api/authors/{author_serial}/entries/{entry_serial}/comments/",
        "page_number": page,
        "size": size,
        "count": total_entry_comments,
        "src": serializer.data,
    })
    
@api_view(["GET"])
def get_entry_comments_by_fqid(request, entry_fqid):
    # Source: https://stackoverflow.com/questions/71771838/python-urllib-url-quote-unquote-issue
    # Date Accessed: March 15, 2026
    #fqid is percent enncoded URL
    #unquote converts it back to http
    #without it, django gonna look for an entry with a %-encoded url and that doesnt
    #match anything in our db
    from urllib.parse import unquote
    entry_fqid = unquote(entry_fqid)
    
    entry = get_object_or_404(Entry, fqid=entry_fqid)
    
    visibility_error = check_entry_visibility(request, entry)
    
    if visibility_error:
        return visibility_error
    
    entry_comments = Comment.objects.filter(entry=entry)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_entry_comments = entry_comments.count()
    entry_comments = entry_comments[start_page:end_page]
    serializer = CommentSerializer(entry_comments, many=True)
    
    return Response({
        "type": "comments",
        "web": f"{settings.BACKEND_URL}/authors/{entry.author.uuid}/entries/{entry.serial}/",
        "id": f"{entry_fqid}/comments/",
        "page_number": page,
        "size": size,
        "count": total_entry_comments,
        "src": serializer.data,
        })

# Commented API
@api_view(["GET", "POST"])
def commented(request, author_serial):
    """
    THis function gets all comments on an entry using the author's serial and 
    entry's serial. Visibility is checked before returning to comply with
    the project spec.

    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the entry's author
        entry_serial: UUID of the entry being queried

    Returns:
        Response: comments object containing type, web, id,
                page_number, size, count, and src (list of comment objects).
                Returns 403 if unauthorized, 410 if entry is deleted, 404 if not found.
                All comment objects are paginated as well.
    """
    
    id_type = "FQID" if (author_serial.find("http://") != -1) else "serial"
    if id_type == "serial":
        author = get_object_or_404(Author, uuid=author_serial)
    else:
        author = get_object_or_404(Author, id=author_serial)
    
    if request.method == "GET":
        author_comments = Comment.objects.filter(author=author)
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))
        start_page = (page - 1) * size
        end_page = start_page + size
        total = author_comments.count()
        author_comments = author_comments[start_page:end_page]
        serializer = CommentSerializer(author_comments, many=True)
        return Response({
            "type": "comments",
            "id": f"{settings.BACKEND_URL}/api/authors/{author_serial}/commented/",
            "page_number": page,
            "size": size,
            "count": total,
            "src": serializer.data,
        })
        
    elif request.method == "POST":
        entry_url = request.data.get("entry")
        comment_text = request.data.get("comment")
        
        if not entry_url or not comment_text:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        local_entry = Entry.objects.filter(fqid=entry_url).first()
        
        if not local_entry:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        visibility_error = check_entry_visibility(request, local_entry)
        if visibility_error:
            return visibility_error
        
        comment = Comment.objects.create(
            author=author, 
            entry=local_entry,
            comment=comment_text
            )
        serializer = CommentSerializer(comment)
        
        # Forward comment to entry author's inbox
        # - POST [local] if you post an object of "type":"comment", it will add your comment to the entry whose 
        #   ID is in the entry field
            #- Then the node you posted it to is responsible for forwarding it to the correct inbox
        inbox_url = f"{local_entry.author.host}authors/{local_entry.author.uuid}/inbox"
        try:
            requests.post(inbox_url, json=serializer.data)
        except Exception as e:
            print(f"Failed to forward to inbox: {e}")
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@login_required
def post_comment(request, author_id, entry_serial):
    """
    Purpose: Allows a logged in user to post a comment on an entry via the UI
    """
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            comment = Comment.objects.create(
                author=request.user,
                entry=entry,
                comment=comment_text,
                contentType="text/plain"
            )
            # Forward comment to entry author's inbox
            serializer = CommentSerializer(comment)
            inbox_url = f"{entry.author.host}authors/{entry.author.uuid}/inbox"
            try:
                requests.post(inbox_url, json=serializer.data)
            except Exception as e:
                print(f"Failed to forward to inbox: {e}")
    
    return redirect('munch:display_entry_by_serial', author_id=author_id, entry_serial=entry_serial)