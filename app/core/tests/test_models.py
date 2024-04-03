"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        """Test creating a user with an email is success."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_teacher(self):
        """test creating a teacher."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="First",
            last_name="Last",
        )

        teacher = models.Teacher.objects.create(
            user=user,
            degree="Degree",
        )

        self.assertEqual(str(teacher), f"{user.first_name} {user.last_name}")

    def test_create_course(self):
        """Test creating a course."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="First",
            last_name="Last",
        )

        teacher = models.Teacher.objects.create(
            user=user,
            degree="Degree",
        )

        course = models.Course.objects.create(
            author=teacher, name="Course", description="Course Description"
        )

        self.assertEqual(str(course), course.name)
