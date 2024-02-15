from testing.testcases import TestCase
from notifications.models import Notification
from inbox.services import NotificationService


class NotificationServiceTests(TestCase):

    def setUp(self):
        super(NotificationServiceTests, self).setUp()
        self.linghu = self.create_user('linghu')
        self.dongxie = self.create_user('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_send_comment_notification(self):
        # do not dispatch notification if tweet is commented by tweet creator
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(0, Notification.objects.count())

        # dispatch notification if tweet is commented by others
        comment = self.create_comment(self.dongxie, self.linghu_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(1, Notification.objects.count())

    def test_send_like_notification(self):
        # do not dispatch notification if tweet is liked by tweet creator
        like = self.create_like(self.linghu, self.linghu_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(0, Notification.objects.count())

        # dispatch notification if tweet is liked by others
        like = self.create_like(self.dongxie, self.linghu_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(1, Notification.objects.count())