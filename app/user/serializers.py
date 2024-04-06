"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers
from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    is_teacher = serializers.BooleanField(default=False)
    is_student = serializers.BooleanField(default=False)

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "is_teacher",
            "is_student",
        ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def validate(self, attrs):
        if attrs.get("is_teacher") and attrs.get("is_student"):
            raise serializers.ValidationError(
                "User cannot be both a teacher and a student"
            )
        return attrs

    def create(self, validated_data):
        """Create and return a user with encrypted password."""

        is_teacher = validated_data.pop("is_teacher", False)
        is_student = validated_data.pop("is_student", False)

        user = get_user_model().objects.create_user(**validated_data)

        if is_teacher:
            models.Teacher.objects.create(
                user=user,
                degree=None,
            )

        if is_student:
            models.Student.objects.create(
                user=user,
                gpa=None,
            )

        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
