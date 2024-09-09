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
        """Retrieve all courses"""
        try:
            Teacher.objects.get(user=self.request.user)
            return self.queryset.order_by("-id")
        except Teacher.DoesNotExist:
            raise PermissionDenied(
                "\
                Access denied: Only teachers can access this view.\
                "
            )

    def get_object(self):
        """Retrieve and return the course, ensuring only the author can update or delete."""
        obj = super().get_object()
        teacher = Teacher.objects.get(user=self.request.user)
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            if obj.author != teacher:
                raise PermissionDenied(
                    "You can only update or delete your own courses."
                )
        return obj

    def perform_create(self, serializer):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(author=teacher)
        except Teacher.DoesNotExist:
            raise PermissionDenied("You must be a teacher to create a course.")
