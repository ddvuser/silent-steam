"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
JWT_TOKEN_URL = reverse("user:obtain-token-pair")
JWT_TOKEN_REFRESH_URL = reverse("user:token-refresh")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "First",
            "last_name": "Last",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 8 chars."""
        payload = {
            "email": "test@example.com",
            "password": "test123",
            "first_name": "First",
            "last_name": "Last",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = (
            get_user_model()
            .objects.filter(
                email=payload["email"],
            )
            .exists()
        )
        self.assertFalse(user_exists)

    def test_obtain_token_for_user(self):
        """Test obtain token pair for valid credentials."""
        user_details = {
            "first_name": "First",
            "last_name": "Last",
            "email": "user@example.com",
            "password": "testpass123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = self.client.post(JWT_TOKEN_URL, payload)

        self.assertIn("refresh", res.data)
        self.assertIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_obtain_token_bad_credentials(self):
        """Test return error if credentials is invalid."""
        create_user(email="test@example.com", password="testpass123")

        payload = {"email": "test@example.com", "password": "testpass321"}

        res = self.client.post(JWT_TOKEN_URL, payload)

        self.assertNotIn("refresh", res.data)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_blank_password(self):
        """Test posting a blank password return an error."""
        payload = {"email": "test@example.com", "password": ""}

        res = self.client.post(JWT_TOKEN_URL, payload)

        self.assertNotIn("refresh", res.data)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token(self):
        """Test refreshing a token."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
        }
        create_user(
            email=payload["email"],
            password=payload["password"],
        )

        # Obtain token
        obtain_res = self.client.post(JWT_TOKEN_URL, payload)

        refresh_token = obtain_res.data["refresh"]

        refresh_payload = {"refresh": refresh_token}

        # Refresh token
        refresh_res = self.client.post(JWT_TOKEN_REFRESH_URL, refresh_payload)

        self.assertIn("access", refresh_res.data)
        self.assertNotEqual(
            obtain_res.data["refresh"],
            refresh_res.data["refresh"],
        )
        self.assertNotEqual(
            obtain_res.data["access"],
            refresh_res.data["access"],
        )
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
