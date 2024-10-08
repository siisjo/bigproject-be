from datetime import (
    timedelta,
    datetime
)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from account.models import User

from rest_framework_simplejwt.tokens import AccessToken



class UserRegistrationTests(APITestCase):
    def test_user_signup(self):
        url = reverse('account:signup')
        data = {
            'nationality': 'RepublicOfKorea',
            'work_at': 'Australia',
            'username': 'testuser',
            'nickname': 'testnick',
            'password': 'strongpassword123',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )
        self.url = reverse('account:login')

    def test_login(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.data['nickname'], self.user.nickname)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        data = {
            'email': 'wrongemail@email.com',
            'password': 'blahblah'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )

    def test_logout(self):
        login_url = reverse('account:login')
        logout_url = reverse('account:logout')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 로그아웃 요청
        response = self.client.post(logout_url, {'refresh_token': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=1,
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )
        self.client = APIClient()
        self.url_retrieve = reverse('account:profile')
        self.url_update = reverse('account:profile-update')
        login_url = reverse('account:login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        self.token = access_token

    def test(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile_with_patch(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {
            'username': 'UpdatedName',
            'work_at': 'JAPAN'
        }
        response = self.client.patch(self.url_update, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'UpdatedName')
        self.assertEqual(self.user.work_at, 'JAPAN')


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )
        self.url = reverse('account:password_reset')

    def test_password_reset_reqeust(self):
        data = {
            "email": "testuser@example.com",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_password_reset_request_invalid_email(self):
        response = self.client.post(self.url, {'email': 'invalid@example.com'}, format='json')
        self.assertEqual(response.status_code, 400)


class ActivateUserViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
        )
        self.user.is_active = False

    def test_activate_user_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.uuid))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(reverse("account:account_activate", args=[uid, token]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class RefreshTokenMiddlewareTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@test.com',
            password=make_password('testpassword'),
            username='testuser',
            work_at='test',
            nationality='test',
            is_active=True,
            nickname='test',

        )
        self.client = APIClient()
        self.login_url = reverse('account:login')
        self.refresh_url = reverse('account:token_refresh')

    def test_access_token_refresh(self):
        data = {
            'email': 'test@test.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 200)
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        expired_access_token = AccessToken(access_token)
        expired_access_token.set_exp(from_time=datetime.utcnow() - timedelta(minutes=1))

        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {expired_access_token}'
        self.client.cookies['refresh'] = refresh_token

        auth_response = self.client.post(reverse('account:logout'), {'refresh_token': refresh_token})
        self.assertEqual(auth_response.status_code, status.HTTP_205_RESET_CONTENT)