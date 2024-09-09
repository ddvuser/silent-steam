"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core import models
from django.utils import timezone

CREATE_USER_URL = reverse("user:create")
JWT_TOKEN_URL = reverse("user:obtain-token-pair")
JWT_TOKEN_REFRESH_URL = reverse("user:token-refresh")
RETRIEVE_UPDATE_USER_URL = reverse("user:me")
REQUEST_PASSWORD_RESET_URL = reverse("user:request-pass-reset")


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
            "password_confirmation": "testpass123",
            "first_name": "First",
            "last_name": "Last",
            "is_student": True,
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
            "password_confirmation": "test123",
            "first_name": "First",
            "last_name": "Last",
            "is_student": True,
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

    def test_create_user_without_role(self):
        """
        Test creating a user without providing is_student or is_teacher.
        """
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirmation": "testpass123",
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

    def test_request_password_reset(self):
        """Test requesting password reset succeeds."""
        payload = {
            "email": "test@example.com",
        }
        create_user(email=payload["email"], password="testpass123")

        res = self.client.post(REQUEST_PASSWORD_RESET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check if password reset entry is created
        reset_obj = models.PasswordReset.objects.filter(email=payload["email"]).first()
        self.assertIsNotNone(reset_obj)
        # ensure expiration date set correctly
        self.assertTrue(reset_obj.expires > timezone.now())

    def test_reset_password(self):
        """Test resetting password after requesting it."""
        payload = {
            "email": "test@example.com",
        }
        user = create_user(email=payload["email"], password="testpass123")

        # send a request to reset
        self.client.post(REQUEST_PASSWORD_RESET_URL, payload)

        # get created password reset obj
        reset_obj = models.PasswordReset.objects.filter(email=payload["email"]).first()

        reset_payload = {
            "new_password": "Newpass123@",
            "confirm_password": "Newpass123@",
        }

        reset_url = reverse("user:reset-pass", kwargs={"token": reset_obj.token})
        res = self.client.post(reset_url, reset_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # fetch user again and check if password is updated
        user.refresh_from_db()
        self.assertTrue(user.check_password(reset_payload["new_password"]))

        # check if reset_obj is deleted after reset
        self.assertFalse(
            models.PasswordReset.objects.filter(token=reset_obj.token).exists()
        )


class PrivateUserApiTests(TestCase):
    """Test private features of the user API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_info(self):
        """Test retrieving authenticated user's information."""
        self.client.logout()
        payload = {
            "email": self.user.email,
            "password": "testpass123",
        }

        # Obtain JWT token
        token_res = self.client.post(JWT_TOKEN_URL, payload)
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        token = token_res.data["access"]

        # Add JWT header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Retrieve user's data
        res = self.client.get(RETRIEVE_UPDATE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Validate response contains expected data
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)
        self.assertEqual(res.data["last_name"], self.user.last_name)
        self.assertNotIn("password", res.data)
        self.assertIn("is_teacher", res.data)
        self.assertIn("is_student", res.data)

    def test_retrieve_logged_out_user_info(self):
        """Test retrieving unauthenticated user's information."""
        self.client.logout()

        res = self.client.get(RETRIEVE_UPDATE_USER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_password(self):
        """Test patching user password succeeds"""
        payload = {
            "current_password": "testpass123",
            "new_password": "123testpass",
            "new_password_confirmation": "123testpass",
        }
        res = self.client.patch(RETRIEVE_UPDATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_patch_user_password_fails(self):
        """Test attempt to patch user password fails."""
        payload = {
            "current_password": "wrong_pass",
            "new_password": "123testpass",
            "new_password_confirmation": "123testpass",
        }
        res = self.client.patch(RETRIEVE_UPDATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_info_not_allowed(self):
        """Test put request method is not allowed."""
        payload = {}
        res = self.client.put(RETRIEVE_UPDATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
