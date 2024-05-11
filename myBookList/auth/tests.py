from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        data = {
            'username': 'testuser',
            'email': 'test@mail.com',
            'password': 'testpassword',
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertNotIn('password', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid Credentials')
class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'refresh_token': str(self.refresh_token),
        }
        response = self.client.post('/api/auth/logout/', data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data, {"success": True})

    def test_logout_no_refresh_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Refresh token not provided"})

    def test_logout_unauthenticated(self):
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
