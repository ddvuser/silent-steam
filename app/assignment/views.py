"""
Views for managing Assignments, Submissions and Grades.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.core.exceptions import PermissionDenied
from core.models import Assignment, Submission, Grade, Class
from rest_framework_simplejwt.authentication import JWTAuthentication

from assignment import serializers


class AssignmentViewSet(viewsets.ModelViewSet):
    """View for managing assignment API."""

    serializer_class = serializers.AssignmentSerializer
    queryset = Assignment.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Ensure only teachers can create assignments and validate class ownership."""
        user = self.request.user

        # Ensure the user is a teacher
        if not hasattr(user, "teacher"):
            raise PermissionDenied("You must be a teacher to create an assignment.")

        # Extract class_assigned from the request data
        class_assigned_id = self.request.data.get("class_assigned")

        if class_assigned_id:
            try:
                assigned_class = Class.objects.get(id=class_assigned_id)
            except Class.DoesNotExist:
                raise PermissionDenied("The class does not exist.")

            # Check if the teacher is associated with the class
            if assigned_class.teacher != user.teacher:
                raise PermissionDenied(
                    "You are not authorized to create assignments for this class."
                )

        # Save the assignment
        serializer.save()


class SubmissionViewSet(viewsets.ModelViewSet):
    """View for managing submission API."""

    serializer_class = serializers.SubmissionSerializer
    queryset = Submission.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Allow students to view only their own submissions, and teachers to view submissions for their own classes."""
        user = self.request.user

        if hasattr(user, "student"):
            # Students can only view their own submissions
            return Submission.objects.filter(student=user.student)

        if hasattr(user, "teacher"):
            # Teachers can view submissions related to assignments in their classes
            teacher_classes = Class.objects.filter(teacher=user.teacher)
            assignments = Assignment.objects.filter(class_assigned__in=teacher_classes)
            return Submission.objects.filter(assignment__in=assignments)

        # Raise an error if the user is neither a student nor a teacher
        raise PermissionDenied("Invalid user type")

    def get_object(self):
        """Retrieve an object and ensure students can only access their own submissions."""
        obj = super().get_object()
        user = self.request.user
        if hasattr(user, "student") and obj.student != user.student:
            raise PermissionDenied(
                "You do not have permission to access this submission."
            )
        return obj

    def perform_create(self, serializer):
        """Ensure only students can create submissions."""
        if not hasattr(self.request.user, "student"):
            raise PermissionDenied("You must be a student to submit an assignment.")
        serializer.save()


class GradeViewSet(viewsets.ModelViewSet):
    """View for managing grade API."""

    serializer_class = serializers.GradeSerializer
    queryset = Grade.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Allow teachers to view all grades and students to view only their own."""
        if hasattr(self.request.user, "teacher"):
            # Teachers can view all grades
            return Grade.objects.all()
        elif hasattr(self.request.user, "student"):
            # Students can view only their own grades
            return Grade.objects.filter(submission__student=self.request.user.student)
        raise PermissionDenied("Invalid user type")

    def perform_create(self, serializer):
        """Ensure only teachers can create grades and only for their own assignments."""
        if hasattr(self.request.user, "student"):
            raise PermissionDenied("Students cannot assign grades.")

        if not hasattr(self.request.user, "teacher"):
            raise PermissionDenied("Only teachers can assign grades.")

        submission = serializer.validated_data["submission"]
        assignment = submission.assignment
        teacher = self.request.user.teacher

        # Check if the assignment's class belongs to the teacher
        if assignment.class_assigned.teacher != teacher:
            raise PermissionDenied("You can only grade assignments you created.")

        serializer.save()

    def update(self, request, *args, **kwargs):
        """Prevent students from updating grades."""
        if not hasattr(self.request.user, "teacher"):
            raise PermissionDenied("Only teachers can update grades.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Prevent students from updating grades."""
        if not hasattr(self.request.user, "teacher"):
            raise PermissionDenied("Only teachers can update grades.")
        return super().partial_update(request, *args, **kwargs)
