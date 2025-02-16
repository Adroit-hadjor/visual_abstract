from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class SignupTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_success(self):
        """Test that a user can sign up with valid data."""
        response = self.client.post(
            reverse('signup_htmx'),  # adjust to your signup route
            data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # if using HTMX
        )
        self.assertEqual(response.status_code, 201)  # or 200 if you used that
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_missing_fields(self):
        """Test signup fails if required fields are missing."""
        response = self.client.post(
            reverse('signup_htmx'),
            data={
                'username': '',
                'email': 'nobody@example.com',
                'password': '',
                'password_confirm': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username, password, and confirm password are required', response.content)

    def test_signup_password_mismatch(self):
        """Test signup fails if passwords don't match."""
        response = self.client.post(
            reverse('signup_htmx'),
            data={
                'username': 'user2',
                'email': 'user2@example.com',
                'password': 'test123',
                'password_confirm': 'diff123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Passwords do not match', response.content)


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='secret123'
        )

    def test_login_success(self):
        """Test a valid user can login."""
        response = self.client.post(
            reverse('login_htmx'),  # or your login route
            data={'username': 'testuser', 'password': 'secret123'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully.', response.content)

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        response = self.client.post(
            reverse('login_htmx'),
            data={'username': 'testuser', 'password': 'wrongpass'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials.', response.content)


