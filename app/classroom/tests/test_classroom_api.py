from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from core.models import Class, Course, Teacher, Student
from classroom.serializers import ClassroomSerializer

CLASSROOM_URL = reverse("classroom:classroom-list")


def create_user(**params):
    """Create and return a user."""
    defaults = {
        "email": "user@example.com",
        "password": "testpass123",
        "first_name": "First",
        "last_name": "Last",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


def create_teacher(user, **params):
    """Create and return a teacher."""
    defaults = {
        "degree": "MSc",
    }
    defaults.update(**params)
    return Teacher.objects.create(user=user, **defaults)


def create_student(user, **params):
    """Create and return a student."""
    defaults = {
        "gpa": 3,
    }
    defaults.update(**params)
    return Student.objects.create(user=user, **defaults)


def create_course(author, **params):
    """Create and return a sample course."""
    defaults = {
        "name": "Course Foo",
        "description": "Description of the Course Foo.",
    }
    defaults.update(**params)
    return Course.objects.create(author=author, **defaults)


def create_class(teacher, course, students=None, **params):
    """Create and return a sample class."""
    defaults = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    defaults.update(**params)
    classroom = Class.objects.create(teacher=teacher, course=course, **defaults)
    if students:
        classroom.students.set(students)
    return classroom


class PublicClassroomAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(CLASSROOM_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TeacherClassroomAPITests(TestCase):
    """Test authenticated teacher API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.teacher = create_teacher(user=self.user)
        self.client.force_authenticate(self.user)

    def test_retrieve_classes_created_by_teacher(self):
        """Test retrieving classes created by authenticated teacher."""
        course = create_course(author=self.teacher)
        create_class(teacher=self.teacher, course=course)

        res = self.client.get(CLASSROOM_URL)

        classrooms = Class.objects.filter(teacher=self.teacher)
        serializer = ClassroomSerializer(classrooms, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_class(self):
        """Test creating a class with teacher as the creator."""
        course = create_course(author=self.teacher)
        student = create_student(user=create_user(email="student@example.com"))

        payload = {
            "course": course.id,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "students": [student.id],
        }
        res = self.client.post(CLASSROOM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Class.objects.count(), 1)
        self.assertEqual(Class.objects.get().course, course)

    def test_teacher_cannot_see_other_teachers_classes(self):
        """Test that a teacher cannot see other teachers' classes."""
        other_user = create_user(email="other_teacher@example.com")
        other_teacher = create_teacher(user=other_user)
        course = create_course(author=other_teacher)
        create_class(teacher=other_teacher, course=course)

        res = self.client.get(CLASSROOM_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_teacher_can_create_class(self):
        """Test teacher can create classroom based on courses created by other teachers."""
        other_user = create_user(email="other_teacher@example.com")
        other_teacher = create_teacher(user=other_user)
        course = create_course(author=other_teacher)

        payload = {
            "course": course.id,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "students": [],
        }
        res = self.client.post(CLASSROOM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class StudentClassroomAPITests(TestCase):
    """Test authenticated student API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.student = create_student(user=self.user)
        self.teacher = create_teacher(user=create_user(email="user2@example.com"))
        self.client.force_authenticate(self.user)

    def test_retrieve_classes_enrolled_by_student(self):
        """Test retrieving classes a student is enrolled in."""
        teacher = create_teacher(user=create_user(email="teacher@example.com"))
        course = create_course(author=teacher)
        create_class(teacher=teacher, course=course, students=[self.student])

        res = self.client.get(CLASSROOM_URL)

        classrooms = Class.objects.filter(students=self.student)
        serializer = ClassroomSerializer(classrooms, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_student_cannot_create_class(self):
        """Test that a student cannot create a class."""
        course = create_course(author=self.teacher)
        payload = {
            "course": course.id,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "students": [],
        }
        res = self.client.post(CLASSROOM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
