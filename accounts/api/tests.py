from testing.testcases import TestCase
from rest_framework.test import APIClient
from accounts.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_API = '/api/profiles/{}/'


class AccountAPITest(TestCase):
    def setUp(self):
        self.clear_cache()
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@gmail.com',
            password='correct password',
        )

    def test_login(self):
        # 每个测试函数必须以test_开头，才会被自动调用进行测试
        # 测试必须用post，因为login函数只接受post
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 由于get方法不被允许，所以返回状态码应该是405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # 用了post但是密码错误
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # 验证登录状态为还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # 用了post但是用户名错误
        response = self.client.post(LOGIN_URL, {
            'username': 'notexist',
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Please check input')
        self.assertEqual(response.data['errors']['username'][0], 'User does not exist.')

        # 用了post密码正确
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 返回状态码200 = OK
        self.assertEqual(response.status_code, 200)
        self.assertNotEquals(response.data['user'], None)
        self.assertEqual(response.data['user']['username'], 'admin')
        self.assertEqual(response.data['user']['id'], self.user.id)
        # 验证登录状态为已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # 登录
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # 验证登录状态为已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 用get方法登出
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 用post方法登出
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)

        # 验证登录状态为还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': 'any password',
        }
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@gmail.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # 验证 user profile 已经被创建
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)
        # 验证用户已经登入
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


class UserProfileAPITest(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_update(self):
        linghu, linghu_client = self.create_user_and_client('linghu')
        p = linghu.profile
        p.nickname = 'old nickname'
        p.save()
        url = USER_PROFILE_DETAIL_API.format(p.id)

        # 匿名不可以更新
        response = self.anonymous_client.put(url, {'nickname': 'a new nickname'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual('Authentication credentials were not provided.' in response.data['detail'], True)

        # 别人不可以更新
        _, dongxie_client = self.create_user_and_client('dongxie')
        response = dongxie_client.put(url, {'nickname': 'a new nickname'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual('You do not have permission to access this object' in response.data['detail'], True)

        p.refresh_from_db()
        self.assertEqual(p.nickname, 'old nickname')

        # 自己可以更新
        response = linghu_client.put(url, {'nickname': 'a new nickname'})
        self.assertEqual(response.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'a new nickname')

        # 更新avatar
        response = linghu_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('avatar' in response.data['avatar'], True)
        p.refresh_from_db()
        self.assertIsNotNone(p.avatar)



