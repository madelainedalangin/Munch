from django.conf import settings
from rest_framework import serializers
from .models import *   # replace * with specific models once defined
from django.db import IntegrityError

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

    def isLocal(self, host):
        local_host = f"{settings.BACKEND_URL}/api"
        return host.rstrip('/') == local_host
    
    def create(self, validated_data):
        validated_data.pop('type', None)    # default=None so KeyError isn't raised

        host = validated_data.get('host')
        author_id = validated_data.get('id')
        defaults={
                'uuid': author_id.rsplit('/', 1)[-1],
                'host': host,
                'displayName': validated_data.get('displayName'),
                'github': validated_data.get('github'),
                'profileImage': validated_data.get('profileImage'),
                'web': validated_data.get('web')
        }     
        
        try:
            author = Author.objects.get(id=author_id)
            for field, value in defaults.items():       # update if author exists in database
                setattr(author, field, value)
            author.save

        except Author.DoesNotExist:
            if self.isLocal(host):
                raise serializers.ValidationError(
                    f"Local author {author_id} not found. "
                )
            else:
                author = Author.objects.create_user_stub(**validated_data)

        return author

class FollowRequestSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='follow')
    summary = serializers.SerializerMethodField()
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['type', 'summary', 'actor', 'object']

    def create(self, validated_data):
        actor_data = validated_data.pop('actor')
        object_data = validated_data.pop('object')

        actor_author = AuthorSerializer().create(actor_data)
        object_author = AuthorSerializer().create(object_data)

        return Follow.objects.create(
            actor=actor_author,
            object=object_author
        )
    
    def get_summary(self, obj):
        return f"{obj.actor.displayName} wants to follow {obj.object.displayName}"

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=100, default='like')
    author = AuthorSerializer()
    id = serializers.URLField(source='fqid')
    object = serializers.URLField(source='object_url')

    class Meta:
        model = Like
        fields = ['type', 'author', 'published', 'id', 'object']
    
    def create(self, validated_data):
        """
        This is called when doing serializer.save() after validating incoming
        data.
        
        Defines how to turn the validated incoming JSON into a saved model
        instance
        """
        validated_data.pop('type', None)
        author_data = validated_data.pop('author')
        author = AuthorSerializer().create(author_data)
        try:
            return Like.objects.create(
                author=author,
                published=validated_data.get('published'),
                object_url=validated_data.get('object_url')
            )
        except IntegrityError:
            raise serializers.ValidationError("Already liked.")

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
    entry = serializers.CharField()
    
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
        likes = Like.objects.filter(object_url=obj.fqid).order_by("-published")
        return {
            "type": "likes",
            "id": f"{obj.fqid}/likes",
            "web": f"{settings.BACKEND_URL}/authors/{obj.entry.author.uuid}/entries/{obj.entry.serial}/",
            "page_number": 1,
            "size": likes.count(),
            "count": likes.count(),
            "src": LikeSerializer(likes, many=True).data,
        }
        
    def to_representation(self, obj):
        rep = super().to_representation(obj)
        rep['entry'] = obj.entry.fqid  # always output the FQID on GET
        return rep

    def create(self, validated_data):
        validated_data.pop('type', None)
        author_data = validated_data.pop('author')
        author = AuthorSerializer().create(author_data)
        entry_fqid = validated_data.pop('entry')
        try:
            entry = Entry.objects.get(fqid=entry_fqid)
        except Entry.DoesNotExist:
            raise serializers.ValidationError(f"Entry {entry_fqid} not found.")
        return Comment.objects.create(
            author=author,
            entry=entry,
            comment=validated_data.get('comment'),
            contentType=validated_data.get('contentType', 'text/plain'),
            published=validated_data.get('published'),
        )
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
    
    #Removed read_only=True from id and web so the incoming id and web fields 
    # actually land in validated_data as fqid and url.
    #also will help when writing tests for test_inbox
    id = serializers.URLField(source='fqid', required=False)
    web = serializers.URLField(source='url', required=False)
    
    author = AuthorSerializer(required=False, allow_null=True, default=None)
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
        comments = Comment.objects.filter(entry=obj).order_by("-published")
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
        likes = Like.objects.filter(object_url=obj.fqid).order_by("-published")
        return {
            "type": "likes",
            "id": f"{obj.fqid}/likes",
            "web": f"{settings.BACKEND_URL}/authors/{obj.author.uuid}/entries/{obj.serial}/",
            "page_number": 1,
            "size": likes.count(),
            "count": likes.count(),
            "src": LikeSerializer(likes, many=True).data,
        }
    
    def create(self, validated_data):
        validated_data.pop("type", None)
        author_data = validated_data.pop("author", None)
        if author_data is not None:
            if isinstance(author_data, Author):
                # passed directly as an object via serializer.save(author=request.user)
                validated_data["author"] = author_data
            else:
                # incoming JSON from remote node inbox
                validated_data["author"] = AuthorSerializer().create(author_data)
        fqid = validated_data.pop("fqid", None)
        url = validated_data.pop("url", None)
        entry = Entry.objects.create(**validated_data)
        if fqid:
            entry.fqid = fqid
            entry.url = url or fqid
            entry.save()
        return entry
        
class EntriesSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, default='entries')
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = EntrySerializer(many=True)

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['url', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_url(self, value):
        return value.rstrip('/')
