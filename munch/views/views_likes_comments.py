from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import IntegrityError # for liked function

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *
from munch.views.views_utils import check_entry_visibility
from munch.authentication import ServerBasicAuthentication
from munch.permissions import IsAuthorizedServer

import requests
from urllib.parse import unquote
from requests import post as requests_post, RequestException
from munch.views.views_posting import get_inboxs
import re

def like_distribute(like, inbox_urls):
    serializer = LikeSerializer(like)
    data = serializer.data
    
    for inbox_url in inbox_urls:
        try:
            match = re.match(r'^(https?://[^/]+)', inbox_url)
            if not match:
                continue
            node_base_url = match.group(1)
            try:
                server = Server.objects.get(url=node_base_url)
                outgoing_auth = (server.username, server.password)
            except Server.DoesNotExist:
                continue
            requests_post(inbox_url, auth=outgoing_auth, json=data)
        except RequestException:
            continue

def comment_distribute(comment, inbox_urls):
    serializer = CommentSerializer(comment)
    data = serializer.data
    
    for inbox_url in inbox_urls:
        try:
            match = re.match(r'^(https?://[^/]+)', inbox_url)
            if not match:
                continue
            node_base_url = match.group(1)
            try:
                server = Server.objects.get(url=node_base_url)
                outgoing_auth = (server.username, server.password)
            except Server.DoesNotExist:
                continue
            requests_post(inbox_url, auth=outgoing_auth, json=data)
        except RequestException:
            continue



@api_view(["GET"])
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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

    entry_likes = Like.objects.filter(object_url=entry.fqid).order_by("-published")
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
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_entry_likes_by_fqid(request, entry_fqid):
    # Source: https://stackoverflow.com/questions/71771838/python-urllib-url-quote-unquote-issue
    # Date Accessed: March 15, 2026

    #fqid is percent enncoded URL
    #unquote converts it back to http
    #without it, django gonna look for an entry with a %-encoded url and that doesnt
    #match anything in our db
    
    entry_fqid = unquote(entry_fqid)
    
    entry = get_object_or_404(Entry, fqid=entry_fqid)
    
    visibility_error = check_entry_visibility(request, entry)
    
    if visibility_error:
        return visibility_error
    
    entry_likes = Like.objects.filter(object_url=entry.fqid).order_by("-published")
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_entry_likes = entry_likes.count()
    entry_likes = entry_likes[start_page:end_page]
    serializer = LikeSerializer(entry_likes, many=True)
    
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
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
def get_comment_likes(request, author_serial, entry_serial, comment_fqid):
    """
    GET api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{COMMENT_FQID}/likes/
    This function gets likes on a specific comment. The likes is a list and is
    paginated.
    
    Visibility based on the parent entry's visibility settings.
    
    Args:
        request: HTTP GET request from the client
        author_serial: UUID of the comment's author
        entry_serial: UUID of the parent entry
        comment_fqid: FQID of the comment being queried

    Returns: 
        Response: A paginated likes object containing type, web, id,
        page_number, size, count, and src (list of like objects).
        
        - Returns 403 if unauthorized, 410 if parent entry is deleted.
    """
    comment_fqid = unquote(comment_fqid)
    entry = get_object_or_404(Entry, serial=entry_serial)
    
    
    comment = get_object_or_404(Comment, entry=entry, fqid=comment_fqid)
    
    visibility_error = check_entry_visibility(request, comment.entry)
    if visibility_error:
        return visibility_error
    
    comment_likes = Like.objects.filter(object_url=comment.fqid).order_by("-published")
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 5))
    start_page = (page - 1) * size
    end_page = start_page + size
    total_comment_likes = comment_likes.count()
    comment_likes = comment_likes[start_page:end_page]
    serializer = LikeSerializer(comment_likes, many=True)
    
    author_str = f"authors/{author_serial}"
    entries_str = f"entries/{entry_serial}"
    comments_str = f"comments/{comment_fqid}"
    
    return Response({
        "type": "likes",
        "web": f"{settings.BACKEND_URL}/{author_str}/{entries_str}/{comments_str}/",
        "id": f"{settings.BACKEND_URL}/api/authors/{author_str}/{entries_str}/{comments_str}/likes/",
        "page_number": page,
        "size": size,
        "count": total_comment_likes,
        "src": serializer.data,
        })


# Liked API

@api_view(["GET", "POST", "DELETE"])
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
        author_likes = Like.objects.filter(author=author).order_by("-published")
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
            inbox_urls = set()

            if "entries" in object_url:
                entry = Entry.objects.filter(fqid=object_url).first()
                if entry:
                    inbox_urls.update(get_inboxs(entry,entry.author))
                    # make sure the entry author gets it too
                    inbox_urls.add(f"{entry.author.id.rstrip('/')}/inbox")
                else:
                    match = re.match(r'(.*?/api/authors/[^/]+)', object_url)
                    if match:
                        inbox_urls.add(f"{match.group(1).rstrip('/')}/inbox")
    
                    
            else:
                comment = Comment.objects.filter(fqid=object_url).first()
                if comment:
                    inbox_urls.update(get_inboxs(comment.entry,comment.entry.author))
                    # make sure comment author gets it
                    inbox_urls.add(f"{comment.author.id.rstrip('/')}/inbox")
                    # optional: also notify entry author
                    inbox_urls.add(f"{comment.entry.author.id.rstrip('/')}/inbox")

            like_distribute(like,list(inbox_urls))
            
        except Exception as e:
            print(f"Failed to forward like notification to inbox: {e}")
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # DELETE request was added on top of user stories for better user experience
    elif request.method == "DELETE":
        object_url = request.data.get("object")
        like = get_object_or_404(Like, author=author, object_url=object_url)
        like.delete()
        return Response({"detail": "Like successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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


# Comments API

@api_view(["GET"])
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
    
    entry_comments = Comment.objects.filter(entry=entry).order_by("-published")
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
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
    
    entry_comments = Comment.objects.filter(entry=entry).order_by("-published")
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
@authentication_classes([ServerBasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthorizedServer | IsAuthenticated])
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
        author_comments = Comment.objects.filter(author=author).order_by("-published")
        
        if isinstance(request.successful_authenticator, ServerBasicAuthentication):
            author_comments = author_comments.filter(
                entry__visibility__in=['PUBLIC', 'UNLISTED']
            )
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
        if not (IsAuthenticated().has_permission(request, None) or IsAuthorizedServer().has_permission(request, None)):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Not authorized'})

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
            comment=comment_text,
            contentType="text/plain"
            )
        serializer = CommentSerializer(comment)
        
        # Forward comment to entry author's inbox
        # - POST [local] if you post an object of "type":"comment", it will add your comment to the entry whose 
        #   ID is in the entry field
            #- Then the node you posted it to is responsible for forwarding it to the correct inbox

        inbox_urls = get_inboxs(comment.entry,comment.entry.author)
        comment_distribute(comment,inbox_urls)
    
            
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
            inbox_urls = get_inboxs(comment.entry,comment.entry.author)
            comment_distribute(comment,inbox_urls)
    
    return redirect('munch:display_entry_by_serial', author_id=author_id, entry_serial=entry_serial)