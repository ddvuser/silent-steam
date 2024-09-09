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


def create_teacher(user):
    """Create and return a teacher instance."""
    return Teacher.objects.create(user=user)


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
        self.teacher = create_teacher(user=self.user)
        self.client.force_authenticate(self.user)

    def test_retrieve_created_courses_by_me(self):
        """
        Test retrieving a list of created courses by authenticated teacher.
        """
        create_course(author=self.teacher)
        create_course(author=self.teacher)

        res = self.client.get(COURSES_URL)

        courses = Course.objects.filter(author=self.teacher).order_by("-id")
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_all_courses_is_visible_to_teacher(self):
        """Test all courses is visible when retrieving."""

        other_user = create_user(email="user2@example.com")
        other_teacher = create_teacher(user=other_user)

        create_course(author=other_teacher)
        create_course(author=other_teacher, **{"name": "Course Bar"})

        res = self.client.get(COURSES_URL)

        courses = Course.objects.filter(author=self.teacher)
        serializer = CourseSerializer(courses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.data, serializer.data)
        self.assertEqual(
            res.data,
            CourseSerializer(
                Course.objects.all().order_by("-id"),
                many=True,
            ).data,
        )

    def test_teacher_can_create_course(self):
        """Ensure teacher can create a course."""
        payload = {"name": "New Course", "description": "New Course Description"}
        res = self.client.post(COURSES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_teacher_can_update_own_course(self):
        """Ensure teacher can update their own course."""
        course = create_course(author=self.teacher, name="Old Course Name")
        payload = {"name": "Updated Course Name", "description": "Updated Description"}
        url = reverse("course:course-detail", args=[course.id])
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, "Updated Course Name")

    def test_teacher_can_delete_own_course(self):
        """Ensure teacher can delete their own course."""
        course = create_course(author=self.teacher)
        url = reverse("course:course-detail", args=[course.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_teacher_cannot_delete_other_courses(self):
        """Ensure teacher cannot delete other courses."""
        other_user = create_user(email="user2@example.com")
        other_teacher = create_teacher(user=other_user)

        course = create_course(author=other_teacher)
        url = reverse("course:course-detail", args=[course.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(id=course.id).exists())

    def test_student_cannot_create_course(self):
        """Ensure student cannot create a course."""
        student_user = create_user(email="student@example.com")
        self.client.force_authenticate(student_user)

        payload = {"name": "New Course", "description": "New Course Description"}
        res = self.client.post(COURSES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_list_courses(self):
        """Ensure student cannot list courses."""
        student_user = create_user(email="student@example.com")
        self.client.force_authenticate(student_user)

        res = self.client.get(COURSES_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
