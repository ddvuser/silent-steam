"""
Serializer for course API.
"""

from rest_framework import serializers

from core.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for courses."""

    class Meta:
        model = Course
        fields = ["id", "name", "description", "created", "modified"]
        read_only_fields = ["id"]
