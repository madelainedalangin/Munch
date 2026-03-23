from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *
from munch.authentication import ServerBasicAuthentication
from munch.permissions import IsAuthorizedServer


# Inbox API

@api_view(['POST'])
@authentication_classes([ServerBasicAuthentication])
@permission_classes([IsAuthorizedServer])
def inbox(request, target_serial):
    payload_type = request.data.get('type')

    if payload_type == 'follow':
        serializer = FollowRequestSerializer(data=request.data)
    
    elif payload_type == 'entry':
        author_data = request.data.get('author', {})
        author_fqid = author_data.get('id')

        if not author_fqid:
            return Response(
                {"detail": "Entry author is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        author = Author.objects.filter(id=author_fqid).first()

        if author is None:
            author = Author.objects.create(
                id=author_fqid,
                host=author_data.get('host'),
                displayName=author_data.get('displayName'),
                github=author_data.get('github'),
                profileImage=author_data.get('profileImage'),
                web=author_data.get('web') or author_fqid.replace('/api/', '/'),
            )

        existing_entry = Entry.objects.filter(fqid=request.data.get("id")).first()

        if existing_entry:
            serializer = EntrySerializer(existing_entry, data=request.data)
        else:
            serializer = EntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif payload_type == 'comment':
        serializer = CommentSerializer(data=request.data)

    elif payload_type == 'like':
        serializer = LikeSerializer(data=request.data)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)