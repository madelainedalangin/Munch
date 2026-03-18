from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *
from munch.forms import EntryForm
from munch.views.views_utils import check_entry_visibility

import base64 #for image_entry api

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
    
    # TODO - cancel button
    # TODO - if the filled form is invalid, redirct user back to entry details and show error

    if request.user.uuid != entry.author.uuid:
        return HttpResponse({"detail": "Only the author can update this entry."}, status=status.HTTP_403_FORBIDDEN)

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
    
    # pagination for comments
    page = int(request.GET.get('page', 1))
    size = 5
    start = (page - 1) * size
    end = start + size
    all_comments = Comment.objects.filter(entry=entry).order_by("-published")
    total_comments = all_comments.count()
    comments = all_comments[start:end]
    total_pages = (total_comments + size - 1) // size

    comments = list(all_comments[start:end])
    for comment in comments:
        comment.like_count = Like.objects.filter(object_url=comment.fqid).count()
        comment.user_liked = Like.objects.filter(
            author=request.user,
            object_url=comment.fqid
        ).exists() if request.user.is_authenticated else False
        #print(f"comment: {comment.serial}, like_count: {comment.like_count}")

    context = {
        "entry": entry,
        "comments": comments,
        "page": page,
        "total_pages": total_pages,
        "total_comments": total_comments,
    }

    # superuser bypass
    if request.user.is_superuser:
        return render(request, "munch/entry_detail.html", context)

    if request.user == author:
        if entry.visibility == 'DELETED':
            return HttpResponse(status=410)
        return render(request, "munch/entry_detail.html", context)

    # If a user is logged in and has the link to a PUBLIC or UNLISTED post, let them see it.
    if entry.visibility in ['PUBLIC', 'UNLISTED']:
        return render(request, "munch/entry_detail.html", context)

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

    return render(request, "munch/entry_detail.html", context)

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
        entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
        if not request.user.is_authenticated or request.user != entry.author:
            return Response(
                {"detail": "Only the author can update this entry."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
        if not request.user.is_authenticated or request.user != entry.author:
            return Response(
                {"detail": "Only the author can update this entry."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if entry.visibility == "DELETED":
            return Response({"detail": "Entry already deleted."},status=status.HTTP_204_NO_CONTENT)
        entry.visibility = "DELETED"
        entry.save()
        
        return Response({"detail": "Entry successfully deleted."},status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def manage_entry_by_FQID(request, entry_FQID):
    entry = get_object_or_404(Entry, fqid=entry_FQID)

    visibility_error = check_entry_visibility(request, entry)
    if visibility_error:
        return visibility_error
    
    serializer = EntrySerializer(entry)
    return Response(serializer.data,status=status.HTTP_200_OK)

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
                        }, status=status.HTTP_200_OK)
    
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
