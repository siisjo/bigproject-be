import jwt

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from account.models import User
from bigproject.settings import SECRET_KEY


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
        print(response.data)

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
            work_at='testwork'
        )

    def test_login(self):
        url = reverse('account:login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork'
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
            work_at='testwork'
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
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'UpdatedName')
        self.assertEqual(self.user.work_at, 'JAPAN')
