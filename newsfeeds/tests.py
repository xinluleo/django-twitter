from testing.testcases import TestCase
from newsfeeds.services import NewsFeedService
from utils.redis_client import RedisClient
from twitter.cache import USER_NEWSFEEDS_PATTERN
from newsfeeds.tasks import fanout_newsfeeds_main_task
from newsfeeds.models import NewsFeed


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.dongxie = self.create_user('dongxie')

    def test_get_user_newsfeeds(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.dongxie, f'tweet {i}')
            newsfeed = self.create_newsfeed(self.linghu, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        RedisClient.clear()
        conn = RedisClient.get_connection()

        # cache miss
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)

        # cache hit
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)

        # cache updated
        tweet = self.create_tweet(self.linghu, 'a new tweet')
        new_newsfeed = self.create_newsfeed(self.linghu, tweet)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        newsfeed_ids.insert(0, new_newsfeed.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        feed1 = self.create_newsfeed(self.linghu, self.create_tweet(self.linghu))

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.linghu.id)
        self.assertEqual(conn.exists(key), False)
        feed2 = self.create_newsfeed(self.linghu, self.create_tweet(self.linghu))
        self.assertEqual(conn.exists(key), True)

        # verify that push_newsfeed_to_cache is called
        feeds = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual([f.id for f in feeds], [feed2.id, feed1.id])


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.dongxie = self.create_user('dongxie')

    def test_fanout_main_task(self):
        # create 1st tweet that will be fanned out to dongxie.
        tweet = self.create_tweet(self.linghu)
        self.create_friendship(self.dongxie, self.linghu)
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(1 + 1, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 1)

        # create 2nd tweet that will be fanned out to dongxie and 2 new users.
        for i in range(2):
            user = self.create_user('user{}'.format(i))
            self.create_friendship(user, self.linghu)
        tweet = self.create_tweet(self.linghu, 'tweet 2')
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(4 + 2, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 2)

        # create 3rd tweet that will be fanned out to all 4 users (3 existing and 1 new).
        user = self.create_user('another user')
        self.create_friendship(user, self.linghu)
        tweet = self.create_tweet(self.linghu, 'tweet 3')
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created.')
        self.assertEqual(8 + 3, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedService.get_cached_newsfeeds(self.dongxie.id)
        self.assertEqual(len(cached_list), 3)