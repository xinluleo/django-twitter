from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class TweetTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.tweet = self.create_tweet(self.linghu, content="linghu's test tweet")

    def test_hours_to_now(self):
        self.user = User.objects.create(
            username='test',
            password='test',
        )
        tweet = Tweet.objects.create(
            user=self.user,
            content='tweet test',
        )
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        # 测试可以成功创建 photo 的数据对象
        photo = TweetPhoto.objects.create(
            user=self.linghu,
            tweet=self.tweet,
        )
        self.assertEqual(photo.user, self.linghu)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

    def test_cache_tweets_in_redis(self):
        tweet = self.create_tweet(self.linghu)
        conn = RedisClient.get_connection()

        # Test DjangoModelSerializer for caching tweet in Redis.
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)

        data = conn.get(f'tweet:not_exist')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(cached_tweet, tweet)
