from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *

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
        fqid = f"{settings.BACKEND_URL}/api/authors/{author_id}"
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