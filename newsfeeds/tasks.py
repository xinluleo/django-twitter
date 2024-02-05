from celery import shared_task
from friendships.services import FriendshipsService
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR
from tweets.models import Tweet


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    # import 写在里面避免循环依赖
    from newsfeeds.services import NewsFeedService

    # 1. Get all followers
    # 2. Insert the newsfeed into Redis
    # 3. Batch get the newsfeed
    # 4. Fanout the newsfeed to all followers
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipsService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)