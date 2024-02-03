from friendships.services import FriendshipsService
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        # 1. Get all followers
        # 2. Insert the newsfeed into Redis
        # 3. Batch get the newsfeed
        # 4. Fanout the newsfeed to all followers
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipsService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        redis_key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(redis_key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        redis_key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(redis_key, newsfeed, queryset)