from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *
from munch.authentication import ServerBasicAuthentication
from munch.permissions import IsAuthorizedServer

import requests
import re
from urllib.parse import urlparse

def followers_view(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)   # use fqid in future
    follower_list = Author.objects.filter(following_relations__object=author, following_relations__status='accepted')
    #remote authors have no username (displays @None right now) so use
    #their heroku hostname link
    for follower in follower_list:
        follower.handle = urlparse(follower.web).netloc
        
    context = {
        "author": author,
        "followers": follower_list
    }
    return render(request, 'munch/followers.html', context)

def list_following(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)
    following_list = Author.objects.filter(follower_relations__actor=author, follower_relations__status='accepted')
    context = {
        "author": author,
        "following": following_list
    }
    return render(request, 'munch/following_list.html', context)

def list_follow_requests(request, author_uuid):
    author = Author.objects.get(uuid=author_uuid)
    follower_list = Author.objects.filter(following_relations__object=author, following_relations__status='requesting')
    context = {
        "author": author,
        "followers": follower_list
    }
    return render(request, 'munch/follow_request_list.html', context)

@login_required
def connect(request):
    author = Author.objects.get(id=request.user.id)
    following_ids = Author.objects.filter(
        follower_relations__actor=author, 
        following_relations__status='accepted'
    ).values_list('id', flat=True)
    suggestions = Author.objects.exclude(id__in=following_ids).exclude(id=request.user.id)

    context = {
        "suggested_authors": suggestions,
    }
    return render(request, 'munch/connect.html', context)


# Following API

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_following(request, author_serial):
    author = Author.objects.get(uuid=author_serial)

    # get authors that are in a follower_relations relation with the specified actor
    following = Author.objects.filter(follower_relations__actor=author)

    if following:
        serializer = AuthorSerializer(following, many=True)
        return Response(serializer.data)
    
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET', 'DELETE', 'PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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

        # capture group 1: 0+ chars as few as possible until serial
        # capture group 2: 1+ chars until /
        regex_match = re.search(r'^(.*?api\/authors\/)([^/]+)', target_FQID)
        target_service = regex_match.group(1)
        target_serial = regex_match.group(2)

        isLocalAuthor = (target_service == f"{settings.BACKEND_URL}/api/authors/")

        # create follow object if none exists yet
        if follow_entry == None:

            target_author = Author.objects.filter(id=target_FQID).first()
            if target_author is None:
                # TODO request user data from other nodes in future milestones
                return Response(
                    {
                        "detail": "Remote author cannot be found. Add them from via admin first"  
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            actor_author = Author.objects.get(id=f"{settings.BACKEND_URL}/api/authors/{author_serial}")

            follow_entry = Follow.objects.create(
                actor=actor_author,
                object=target_author,
                status='requesting'
            )

        serializer = FollowRequestSerializer(follow_entry)

        if isLocalAuthor:
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            response = requests.post(f"{target_service}{target_serial}/inbox", auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD), json=serializer.data, headers={'Origin':settings.BACKEND_URL})

            if response.status_code == 201:

                # assume accepted
                follow_entry.status = 'accepted'
                follow_entry.save()

                return Response(response.json(), status=status.HTTP_201_CREATED)
            
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


# Followers API

@api_view(['GET', 'DELETE', 'PUT'])
@authentication_classes([SessionAuthentication, ServerBasicAuthentication])
@permission_classes([IsAuthenticated | IsAuthorizedServer])
def manage_follower(request, author_serial, target_FQID):
    
    if request.method == 'GET':
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial, status='accepted').first()

        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if not IsAuthenticated().has_permission(request, None):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Not authorized'})

        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial).first()
        if follow_entry != None:
            follow_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        if not IsAuthenticated().has_permission(request, None):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Not authorized'})
        
        follow_entry = Follow.objects.filter(actor__id=target_FQID, object__uuid=author_serial).first()
        if follow_entry == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        follow_entry.status = 'accepted'
        follow_entry.save()

        serializer = FollowRequestSerializer(follow_entry)
        return Response(serializer.data)


# Follow Request API

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_follow_requests(request, author_serial):
    author = Author.objects.get(id=f"{settings.BACKEND_URL}/api/authors/{author_serial}")

    # get authors that are requesting to follow given author
    follow_requests = Author.objects.filter(following_relations__object=author, following_relations__status='requesting')

    if follow_requests:
        serializer = AuthorSerializer(follow_requests, many=True)
        return Response(serializer.data)
    
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
