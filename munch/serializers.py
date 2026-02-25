from rest_framework import serializers
from .models import *   # replace * with specific models once defined

# API objects in project description

class AuthorSerializer(serializers.Serializer):
    pass

class FollowRequestSerializer(serializers.Serializer):
    pass

class EntrySerializer(serializers.Serializer):
    pass

class EntriesSerializer(serializers.Serializer):
    pass

class CommentSerializer(serializers.Serializer):
    pass

class CommentsSerializer(serializers.Serializer):
    pass

class LikeSerializer(serializers.Serializer):
    pass

class LikesSerializer(serializers.Serializer):
    pass