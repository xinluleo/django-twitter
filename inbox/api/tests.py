from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        super(NotificationTests, self).setUp()
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


class NotificationsAPITest(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_unread_count(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.linghu_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.dongxie_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        # mark_url can only be accessed by POST method
        response = self.linghu_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        # user can only mark his own notifications as read
        response = self.dongxie_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)

        response = self.linghu_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户无法访问notifications api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # dongxie 看不到任何 notification
        response = self.dongxie_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # linghu 可以看到两个 notification
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # 标记之后可以看到一个未读 notification
        notification = self.linghu.notifications.first()
        notification.unread = False
        notification.save()
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.linghu.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # post method is not allowed
        response = self.linghu_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)

        # anonymous user cannot update the notification
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)

        # logged in other user cannot access the notification
        response = self.dongxie_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)

        # mark the notification as read
        response = self.linghu_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # mark the notification as unread
        response = self.linghu_client.put(url, {'unread': True})
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # cannot update the notification with a different verb
        response = self.linghu_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)

        # cannot update other fields
        response = self.linghu_client.put(url, {'actor_content_type': 'newtype', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEquals(notification.actor_content_type, 'newtype')