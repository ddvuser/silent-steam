"""
Database models.
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Student(models.Model):
    """Represents a student."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
    )

    def __str__(self):
        return str(self.id)


class Teacher(models.Model):
    """Represents a teacher."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    degree = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Course(models.Model):
    """Represents a course offered to a student."""

    author = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Class(models.Model):
    """Represents a class."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="classes_taught",
    )
    students = models.ManyToManyField(
        Student,
        related_name="classes_enrolled",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Class {self.id}"


class Assignment(models.Model):
    """Represents an assignment."""

    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()


class Submission(models.Model):
    """Represents a submission of an assignment by a student."""

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="submissions/")


class Grade(models.Model):
    """Represents a grade given to a submission."""

    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    grade = models.FloatField()
