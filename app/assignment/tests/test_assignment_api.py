from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import tempfile

from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Class, Assignment, Submission, Grade, Teacher, Student, Course


User = get_user_model()

ASSIGNMENTS_URL = reverse("assignment:assignment-list")
SUBMISSIONS_URL = reverse("assignment:submission-list")
GRADES_URL = reverse("assignment:grade-list")


def create_user(**params):
    """Create and return a user."""
    defaults = {
        "email": "user@example.com",
        "password": "testpass123",
        "first_name": "First",
        "last_name": "Last",
    }
    defaults.update(**params)
    return User.objects.create_user(**defaults)


def create_teacher(user):
    """Create and return a teacher instance."""
    return Teacher.objects.create(user=user)


def create_student(user):
    """Create and return a student instance."""
    return Student.objects.create(user=user)


def create_course(author):
    """Create and return course instance."""
    return Course.objects.create(author=author, name="Foo")


def create_class(teacher, course_id, **params):
    """Create and return a sample class."""
    defaults = {
        "course": course_id,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    defaults.update(**params)
    return Class.objects.create(teacher=teacher, **defaults)


def create_assignment(class_assigned, **params):
    """Create and return a sample assignment."""
    defaults = {
        "title": "Homework 1",
        "description": "First homework assignment",
        "due_date": "2024-09-30",
    }
    defaults.update(**params)
    return Assignment.objects.create(class_assigned=class_assigned, **defaults)


def create_submission(assignment, student, **params):
    """Create and return a sample submission."""
    with tempfile.TemporaryDirectory():
        file = SimpleUploadedFile(
            "testfile.txt", b"file content", content_type="text/plain"
        )
        defaults = {
            "file": file,
        }
        defaults.update(**params)
        return Submission.objects.create(
            assignment=assignment, student=student, **defaults
        )


def create_grade(submission, **params):
    """Create and return a sample grade."""
    defaults = {
        "grade": 95.0,
    }
    defaults.update(**params)
    return Grade.objects.create(submission=submission, **defaults)


class PublicAssignmentAPITests(TestCase):
    """Test unauthenticated API requests for assignments."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(ASSIGNMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TeacherAssignmentAPITests(TestCase):
    """Test authenticated Teacher API requests for assignments."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.teacher = create_teacher(user=self.user)
        self.course = create_course(author=self.teacher)
        self.classroom = create_class(teacher=self.teacher, course_id=self.course)
        self.client.force_authenticate(self.user)

    def test_create_assignment_by_teacher(self):
        """Ensure teacher can create an assignment."""
        payload = {
            "class_assigned": self.classroom.id,
            "title": "New Homework",
            "description": "New homework description",
            "due_date": "2024-10-01",
        }
        res = self.client.post(ASSIGNMENTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_teacher_cannot_create_assignment_for_other_classes(self):
        """Ensure teacher cannot create assignments for other classes."""
        course = create_course(author=self.teacher)
        other_class = create_class(
            teacher=create_teacher(user=create_user(email="newuser@example.com")),
            course_id=course,
        )
        payload = {
            "class_assigned": other_class.id,
            "title": "Other Class Homework",
            "description": "Homework for another class",
            "due_date": "2024-10-01",
        }
        res = self.client.post(ASSIGNMENTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StudentSubmissionAPITests(TestCase):
    """Test authenticated Student API requests for submissions."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="student@example.com")
        self.student = create_student(user=self.user)
        self.teacher = create_teacher(user=create_user(email="teacher@example.com"))
        self.course = create_course(author=self.teacher)
        self.classroom = create_class(teacher=self.teacher, course_id=self.course)
        self.assignment = create_assignment(class_assigned=self.classroom)
        self.client.force_authenticate(self.user)

    def test_create_submission_by_student(self):
        """Ensure student can create a submission for the assignment to the class he enrolled."""
        # Enroll student to the class
        self.classroom.students.add(self.student.id)
        with tempfile.TemporaryDirectory():
            file = SimpleUploadedFile(
                "testfile.txt", b"file content", content_type="text/plain"
            )
            payload = {
                "assignment": self.assignment.id,
                "file": file,
                "student": self.student.id,
                "description": "Foo",
                "due_date": "2024-12-31",
            }
            res = self.client.post(SUBMISSIONS_URL, payload, format="multipart")
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Submission.objects.count(), 1)

    def test_create_submission_not_enrolled(self):
        """Ensure student cannot submit if not enrolled in the class."""
        other_student = create_student(
            user=create_user(email="other_student@example.com")
        )

        with tempfile.TemporaryDirectory():
            file = SimpleUploadedFile(
                "testfile.txt", b"file content", content_type="text/plain"
            )
            payload = {
                "assignment": self.assignment.id,
                "student": other_student.id,
                "file": file,
                "description": "Foo",
                "due_date": "2024-12-31",
            }
            res = self.client.post(SUBMISSIONS_URL, payload, format="multipart")
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_create_submission_for_own_assignments(self):
        """Ensure student cannot create a submission for their own assignments."""
        with tempfile.TemporaryDirectory():
            file = SimpleUploadedFile(
                "testfile.txt", b"file content", content_type="text/plain"
            )
            payload = {
                "assignment": self.assignment.id,
                "file": file,
                "student": self.student.id,
                "description": "Foo",
                "due_date": "2024-12-30",
            }
            res = self.client.post(SUBMISSIONS_URL, payload, format="multipart")
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TeacherGradeAPITests(TestCase):
    """Test authenticated Teacher API requests for grades."""

    def setUp(self):
        self.client = APIClient()
        self.teacher = create_teacher(user=create_user(email="teacher@example.com"))
        self.student = create_student(user=create_user(email="student@example.com"))
        self.course = create_course(author=self.teacher)
        self.classroom = create_class(teacher=self.teacher, course_id=self.course)
        self.assignment = create_assignment(class_assigned=self.classroom)
        self.submission = create_submission(
            assignment=self.assignment, student=self.student
        )
        self.client.force_authenticate(self.student.user)

    def test_create_grade_by_teacher(self):
        """Ensure teacher can create a grade."""
        self.client.logout()
        # Authenticate as a teacher
        self.client.force_authenticate(self.teacher.user)
        payload = {"submission": self.submission.id, "grade": 90.0}
        res = self.client.post(GRADES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_student_cannot_create_grade(self):
        """Ensure student cannot create a grade."""
        payload = {"submission": self.submission.id, "grade": 90.0}
        res = self.client.post(GRADES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_only_view_their_grades(self):
        """Ensure students can only view their own grades."""
        res = self.client.get(GRADES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ensure the grade belongs to the logged-in student
        for grade in res.data:
            self.assertEqual(grade["submission"]["student"], self.student.id)

    def test_teacher_can_grade_own_assignments(self):
        """Ensure teacher can grade assignments they created."""
        self.client.force_authenticate(self.teacher.user)
        payload = {"submission": self.submission.id, "grade": 90.0}
        res = self.client.post(GRADES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_teacher_cannot_grade_other_assignments(self):
        """Ensure teacher cannot grade assignments they didn't create."""
        other_teacher = create_teacher(
            user=create_user(email="other_teacher@example.com")
        )
        self.client.force_authenticate(other_teacher.user)
        payload = {"submission": self.submission.id, "grade": 80.0}
        res = self.client.post(GRADES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
