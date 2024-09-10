"""
Views for the classroom APIs.
"""

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.models import Class, Teacher
from classroom import serializers


class ClassroomViewSet(viewsets.ModelViewSet):
    """View for managing classroom API."""

    serializer_class = serializers.ClassroomSerializer
    queryset = Class.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve classrooms depending on user."""
        if hasattr(self.request.user, "teacher"):
            # Teacher sees only their own classes
            return self.queryset.filter(teacher=self.request.user.teacher).order_by(
                "-id"
            )
        elif hasattr(self.request.user, "student"):
            # Student sees only classes they are enrolled in
            return self.queryset.filter(students=self.request.user.student).order_by(
                "-id"
            )
        else:
            raise PermissionDenied(
                "Access denied: Only students or teachers can access this view."
            )

    def perform_create(self, serializer):
        """Create a classroom based on teacher's courses or others' courses."""
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(teacher=teacher)
        except Teacher.DoesNotExist:
            raise PermissionDenied("You must be a teacher to create a classroom.")
