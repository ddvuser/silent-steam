"""
Views for the courses APIs.
"""

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.models import Course, Teacher
from course import serializers


class CourseViewSet(viewsets.ModelViewSet):
    """View for manage course API."""

    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve courses created by authenticated teacher."""
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return self.queryset.filter(author=teacher).order_by("-id")
        except Teacher.DoesNotExist:
            # If user is a student, raise permission denied
            raise PermissionDenied(
                "\
                Access denied: Only teachers can access this view.\
                "
            )

    def perform_create(self, serializer):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(author=teacher)
        except Teacher.DoesNotExist:
            raise PermissionDenied("You must be a teacher to create a course.")
