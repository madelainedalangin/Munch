from rest_framework import serializers
from .models import *   # replace * with specific models once defined

# API objects in project description

class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='author')
    
    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName', 'github', 'profileImage', 'web', 'description']

        # clear validators so it doesn't complain when receiving follow requests
        extra_kwargs = {
            'id': {'validators': []},
            'web': {'validators': []},
        }

class FollowRequestSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='follow')
    summary = serializers.SerializerMethodField()
    actor = AuthorSerializer()
    object = AuthorSerializer()
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Follow
        fields = ['type', 'summary', 'actor', 'object', 'status']

    def create(self, validated_data):
        actor_data = validated_data.pop('actor')
        object_data = validated_data.pop('object')

        actor_author = self.update_or_create(actor_data)
        object_author = self.update_or_create(object_data)

        return Follow.objects.create(
            actor=actor_author,
            object=object_author
        )
    
    def get_summary(self, obj):
        return f"{obj.actor.displayName} wants to follow {obj.object.displayName}"
    
    def update_or_create(self, author_data):
        author, _ = Author.objects.update_or_create(
            id=author_data.get('id'),
            defaults={
                'uuid': author_data.get('id').rsplit('/', 1)[-1],
                'host': author_data.get('host'),
                'displayName': author_data.get('displayName'),
                'github': author_data.get('github'),
                'profileImage': author_data.get('profileImage'),
                'web': author_data.get('web')
            }
        )
        return author

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='like')
    author = AuthorSerializer()
    id = serializers.URLField(source='fqid')
    object = serializers.URLField(source='object_url')

    class Meta:
        model = Like
        fields = ['type', 'author', 'published', 'id', 'object']

class LikesSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='likes')
    web = serializers.SerializerMethodField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = LikeSerializer(many=True)

class CommentSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='comment')
    author = AuthorSerializer()
    web = serializers.SerializerMethodField()
    id = serializers.URLField(source="fqid")
    likes = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            "type",
            "author",
            "comment",
            "contentType",
            "published",
            "id",
            "entry",
            "web",
            "likes"
        ]
        
    def get_entry(self, obj):
        return obj.entry.fqid
    
    def get_web(self, obj):
        return obj.entry.fqid.replace("/api/", "/") #add web field to Entry
    
    def get_likes(self, obj):
        likes = Like.objects.filter(object_url=obj.fqid)
        return {
            "type": "likes",
            "id": f"{obj.fqid}/likes",
            "web": f"{settings.BACKEND_URL}/authors/{obj.entry.author.uuid}/entries/{obj.entry.serial}/",
            "page_number": 1,
            "size": likes.count(),
            "count": likes.count(),
            "src": LikeSerializer(likes, many=True).data,
        }

class CommentsSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='comments')
    web = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = CommentSerializer(many=True)

class EntrySerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='entry', read_only=True)
    id = serializers.URLField(source='fqid', read_only=True)
    web = serializers.URLField(source='url', read_only=True)
    author = AuthorSerializer()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = [
            'type', 
            'title', 
            'id', 
            'web', 
            'description', 
            'contentType', 
            'content', 
            'author', 
            'published', 
            'visibility', 
            'comments', 
            'likes'
            ]

    def get_comments(self, obj):
        comments = Comment.objects.filter(entry=obj)
        return {
            "type": "comments",
            "id": f"{obj.fqid}/comments",
            "web": f"{settings.BACKEND_URL}/authors/{obj.author.uuid}/entries/{obj.serial}/",
            "page_number": 1,
            "size": 5,
            "count": comments.count(),
            "src": CommentSerializer(comments[:5], many=True).data,
        }
    def get_likes(self, obj):
        likes = Like.objects.filter(object_url=obj.fqid)
        return {
            "type": "likes",
            "id": f"{obj.fqid}/likes",
            "web": f"{settings.BACKEND_URL}/authors/{obj.author.uuid}/entries/{obj.serial}/",
            "page_number": 1,
            "size": likes.count(),
            "count": likes.count(),
            "src": LikeSerializer(likes, many=True).data,
        }
class EntriesSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='entries')
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = EntrySerializer(many=True)
