from rest_framework import serializers
from .models import *   # replace * with specific models once defined

# API objects in project description

class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='author')
    id = serializers.URLField(source='fqid')
    host = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()
    web = serializers.URLField()
    
    class Meta:
        model = Author
        fields = ['displayName']

class FollowRequestSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='follow')
    summary = serializers.CharField(max_length=200)
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['actor', 'object']

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='like')
    author = AuthorSerializer()
    id = serializers.URLField(source='fqid')
    object = serializers.URLField()

    class Meta:
        model = Like
        fields = ['author', 'published']

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
        fields = ['author', 'comment', 'contentType', 'published']

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
        fields = ['title', 'description', 'contentType', 'content', 'author', 'published', 'visibility']

class EntriesSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='entries')
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = EntrySerializer(many=True)

class FollowSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer()
    target = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['status', 'actor', 'object']