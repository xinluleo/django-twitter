from comments.models import Comment
from django.test import TestCase as DjangoTestCase
from django.core.cache import caches
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from rest_framework.test import APIClient
from likes.models import Like
from utils.redis_client import RedisClient
from friendships.models import Friendship


class TestCase(DjangoTestCase):

    def clear_cache(self):
        caches['testing'].clear()
        RedisClient.clear()

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # 不能写成 User.objects.create()
        # 因为password需要被加密，username和email需要被小写化
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default content'
        return Tweet.objects.create(
            user=user,
            content=content,
        )

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(
            user=user,
            tweet=tweet,
            content=content,
        )

    def create_like(self, user, target):
        # 这里的 target 可以是 comment 也可以是 tweet
        instance, _  = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance

    def create_user_and_client(self, username, email=None, password=None):
        user = self.create_user(username, email, password)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(
            user=user,
            tweet=tweet,
        )

    def create_friendship(self, from_user, to_user):
        return Friendship.objects.create(from_user=from_user, to_user=to_user)