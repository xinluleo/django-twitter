from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        # 1. Get all followers
        # 2. Insert the newsfeed into Redis
        # 3. Batch get the newsfeed
        # 4. Fanout the newsfeed to all followers
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)