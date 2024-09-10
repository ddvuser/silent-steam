"""
Serializer for classroom API.
"""

from rest_framework import serializers
from core.models import Class, Course, Teacher, Student


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializer for classroom objects."""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), required=False
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), many=True, required=False
    )

    class Meta:
        model = Class
        fields = ["id", "course", "teacher", "students", "start_date", "end_date"]
        read_only_fields = ["id", "teacher"]

    def create(self, validated_data):
        """Override to assign teacher automatically during classroom creation."""
        students = validated_data.pop("students", [])
        classroom = Class.objects.create(**validated_data)
        classroom.students.set(students)
        return classroom
