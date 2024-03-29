from comments.api.serializers import CommentSerializer
from likes.services import LikeService
from likes.api.serializers import LikeSerializer
from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from tweets.constants import TWEET_PHOTOS_UPLOAD_LIMIT
from rest_framework.exceptions import ValidationError
from tweets.services import TweetService
from utils.redis_helper import RedisHelper


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet(source='cached_user')
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'comments_count',
            'likes_count',
            'has_liked',
            'photo_urls',
        )

    def get_comments_count(self, obj):
        return RedisHelper.get_count(obj, 'comments_count')

    def get_likes_count(self, obj):
        return RedisHelper.get_count(obj, 'likes_count')

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_photo_urls(self, obj):
        # 这里的 obj 是 Tweet instance
        # 拿到所有的 photo， 并除去 has_deleted=true的
        photo_queryset = obj.tweetphoto_set.exclude(has_deleted=True)
        # 通过 photo_queryset 可以拿到所有的图片
        photo_urls = [photo.file.url for photo in photo_queryset]
        return photo_urls


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Tweet
        fields = ('content', 'files',)

    def validate(self, data):
        if len(data.get('files', [])) > TWEET_PHOTOS_UPLOAD_LIMIT:
            raise ValidationError({
                'message': f'You can upload {TWEET_PHOTOS_UPLOAD_LIMIT} photos at most'
            })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(
            user=user,
            content=content,
        )
        if validated_data.get('files'):
            TweetService.create_photos_from_files(
                tweet,
                validated_data['files'],
            )

        return tweet


class TweetSerializerWithDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = TweetSerializer.Meta.fields + (
            'comments',
            'likes',
            'has_liked',
            'comments_count',
            'likes_count',
        )