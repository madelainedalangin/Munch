from rest_framework import serializers
from .models import *   # replace * with specific models once defined

# API objects in project description

class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='author')
    
    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName', 'github', 'profileImage', 'web']

class FollowRequestSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='follow')
    summary = serializers.CharField(max_length=200)
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['type', 'summary', 'actor', 'object']

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='like')
    author = AuthorSerializer()
    id = serializers.URLField(source='fqid')
    object = serializers.URLField()

    class Meta:
        model = Like
        fields = ['type', 'author', 'published', 'id', 'object']

class LikesSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='likes')
    web = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = LikeSerializer(many=True)

class CommentSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='comment')
    author = AuthorSerializer()
    id = serializers.URLField(source='fqid')
    entry = serializers.URLField()
    likes = LikesSerializer()

    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType', 'published', 'id', 'entry', 'likes']

class CommentsSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='comments')
    web = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = CommentSerializer(many=True)

class EntrySerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='entry')
    id = serializers.URLField(source='fqid')
    web = serializers.URLField()
    author = AuthorSerializer()
    comments = CommentsSerializer()
    likes = LikesSerializer()


    class Meta:
        model = Entry
        fields = ['type', 'title', 'id', 'web', 'description', 'contentType', 'content', 'author', 'comments', 'likes', 'published', 'visibility']

class EntriesSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='entries')
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = EntrySerializer(many=True)
