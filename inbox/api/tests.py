from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'

class NotificationTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.dongxie_tweet = self.create_tweet(self.dongxie)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.dongxie_tweet.id,
            'content': 'hello dongxie'
        })
        self.assertEqual(1, Notification.objects.count())

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.linghu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.dongxie_tweet.id,
        })
        self.assertEqual(1, Notification.objects.count())