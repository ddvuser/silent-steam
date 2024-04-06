"""
Tests for models.
"""

import os
import tempfile
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(
    email="test@example.com",
    password="testpass123",
    first_name="First",
    last_name="Last",
):
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    return user


class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        """Test creating a user with an email is success."""
        email = "user@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)

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
        user = create_user()

        teacher = models.Teacher.objects.create(
            user=user,
            degree="Degree",
        )

        self.assertEqual(str(teacher), f"{user.first_name} {user.last_name}")

    def test_create_course(self):
        """Test creating a course."""
        user = create_user()

        teacher = models.Teacher.objects.create(
            user=user,
            degree="Degree",
        )

        course = models.Course.objects.create(
            author=teacher, name="Course", description="Course Description"
        )

        self.assertEqual(str(course), course.name)

    def test_create_student(self):
        """Test creating a student."""
        user = create_user()

        test_gpa = Decimal("2.9")
        student_with_gpa = models.Student.objects.create(
            user=user,
            gpa=test_gpa,
        )

        self.assertEqual(str(student_with_gpa), str(student_with_gpa.id))
        self.assertEqual(test_gpa, student_with_gpa.gpa)

        student_no_gpa = models.Student.objects.create(user=user, gpa=None)
        self.assertIsNone(student_no_gpa.gpa)

    def test_create_class(self):
        """Test creating a class for students."""
        user1 = create_user()
        user2 = create_user(email="user2@example.com")
        user3 = create_user(email="teacher@example.com")

        student1 = models.Student.objects.create(user=user1, gpa=None)
        student2 = models.Student.objects.create(user=user2, gpa=None)

        teacher = models.Teacher.objects.create(user=user3, degree="Test")

        course1 = models.Course.objects.create(
            author=teacher,
            name="Math",
            description="Test Math",
        )

        class1 = models.Class.objects.create(
            course=course1,
            teacher=teacher,
            start_date="2024-01-01",
            end_date="2024-06-01",
        )

        class1.students.add(student1, student2)

        self.assertEqual(class1.students.count(), 2)
        self.assertEqual(str(class1), f"Class {class1.id}")
        self.assertIn(student1, class1.students.filter())

    def test_create_assignment(self):
        """Test creating an assignment for class."""

        user3 = create_user(email="teacher@example.com")
        teacher = models.Teacher.objects.create(user=user3, degree="Test")

        course1 = models.Course.objects.create(
            author=teacher,
            name="Math",
            description="Test Math",
        )

        class1 = models.Class.objects.create(
            course=course1,
            teacher=teacher,
            start_date="2024-01-01",
            end_date="2024-06-01",
        )

        assignment = models.Assignment.objects.create(
            class_assigned=class1,
            title="Task1",
            description="Task1 Desc",
            due_date="2024-02-01",
        )

        self.assertEqual(assignment.class_assigned.course.name, course1.name)

    def test_create_submission(self):
        """Test creating a submission for an assignment."""
        user = create_user()
        user3 = create_user(email="teacher@example.com")

        student = models.Student.objects.create(user=user, gpa=None)
        teacher = models.Teacher.objects.create(user=user3, degree="Test")

        course1 = models.Course.objects.create(
            author=teacher,
            name="Math",
            description="Test Math",
        )

        class1 = models.Class.objects.create(
            course=course1,
            teacher=teacher,
            start_date="2024-01-01",
            end_date="2024-06-01",
        )

        assignment = models.Assignment.objects.create(
            class_assigned=class1,
            title="Task1",
            description="Task1 Desc",
            due_date="2024-02-01",
        )

        file_path = "test_submission.txt"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:  # NOQA
            file_path = temp_file.name

        submission = models.Submission.objects.create(
            assignment=assignment, student=student, file=file_path
        )

        self.assertIsNotNone(submission)

        os.remove(file_path)

    def test_create_grade(self):
        """Test creating a grade for a submission."""

        """Test creating a submission for an assignment."""
        user = create_user()
        user3 = create_user(email="teacher@example.com")

        student = models.Student.objects.create(user=user, gpa=None)
        teacher = models.Teacher.objects.create(user=user3, degree="Test")

        course1 = models.Course.objects.create(
            author=teacher,
            name="Math",
            description="Test Math",
        )

        class1 = models.Class.objects.create(
            course=course1,
            teacher=teacher,
            start_date="2024-01-01",
            end_date="2024-06-01",
        )

        assignment = models.Assignment.objects.create(
            class_assigned=class1,
            title="Task1",
            description="Task1 Desc",
            due_date="2024-02-01",
        )

        file_path = "test_submission.txt"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:  # NOQA
            file_path = temp_file.name

        submission = models.Submission.objects.create(
            assignment=assignment, student=student, file=file_path
        )

        grade = models.Grade.objects.create(
            submission=submission,
            grade=2.9,
        )

        self.assertEqual(grade.grade, 2.9)

        os.remove(file_path)
