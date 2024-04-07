"""
Tests for course API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Course, Teacher

from course.serializers import CourseSerializer


COURSES_URL = reverse("course:course-list")


def create_user(**params):
    """Create and return user."""
    defaults = {
        "email": "user@example.com",
        "password": "testpass123",
        "first_name": "First",
        "last_name": "Last",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


def create_course(author, **params):
    """Create and return sample course."""
    defaults = {
        "name": "Course Foo",
        "description": "Description of the Course Foo.",
    }
    defaults.update(**params)

    course = Course.objects.create(author=author, **defaults)
    return course


class PublicCourseAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(COURSES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TeacherCourseAPITests(TestCase):
    """Test authenticated Teacher API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.teacher = Teacher.objects.create(
            user=self.user,
            degree=None,
        )
        self.client.force_authenticate(self.user)

    def test_retieve_created_courses_by_me(self):
        """
        Test retrieving a list of created courses by authenticated teacher.
        """
        create_course(author=self.teacher)
        create_course(author=self.teacher)

        res = self.client.get(COURSES_URL)

        courses = Course.objects.all().order_by("-id")
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_courses_list_limited_to_teacher(self):
        """Test list of courses is limited to authenticated teacher."""

        other_user = create_user(**{"email": "user2@example.com"})
        other_teacher = Teacher.objects.create(user=other_user)

        create_course(author=other_teacher)
        create_course(author=other_teacher)

        res = self.client.get(COURSES_URL)

        courses = Course.objects.filter(author=self.teacher)
        serializer = CourseSerializer(courses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
