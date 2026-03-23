from django.conf import settings

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from munch.serializers import *
from munch.models import *
from munch.authentication import ServerBasicAuthentication
from munch.permissions import IsAuthorizedServer

# Authors API

@api_view(['GET'])
@authentication_classes([SessionAuthentication, ServerBasicAuthentication])
@permission_classes([IsAuthenticated | IsAuthorizedServer])
def get_authors(request):
    authors = Author.objects.filter(host=f"{settings.BACKEND_URL}/api/")
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, ServerBasicAuthentication])
@permission_classes([IsAuthenticated | IsAuthorizedServer])
def get_authors_paginated(request):
    page = request.GET.get('page')
    size = request.GET.get('size')

    if (page != None) and (size != None):
        start = page * size
        end = start + size

        authors = Author.objects.filter(host=f"{settings.BACKEND_URL}/api/")[start:end]
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    elif (page == None) and (size == None):
        authors = Author.objects.filter(host=f"{settings.BACKEND_URL}/api/")
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@authentication_classes([SessionAuthentication, ServerBasicAuthentication])
def get_author(request, author_id):
    id_type = 'FQID' if (author_id.find("http://") != -1) else 'serial'
    fqid = None

    if id_type == 'serial' and IsAuthenticated().has_permission(request, None):
        fqid = f"{settings.BACKEND_URL}/api/authors/{author_id}"
    elif IsAuthorizedServer().has_permission(request, None):
        fqid = author_id

    if fqid == None:
        return Response(data={'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
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