"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # Fields for role assignment
    is_teacher = serializers.BooleanField(default=False)
    is_student = serializers.BooleanField(default=False)

    # Fields for password handling
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    new_password_confirmation = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "password_confirmation",
            "current_password",
            "new_password",
            "new_password_confirmation",
            "first_name",
            "last_name",
            "is_teacher",
            "is_student",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "password_confirmation": {"write_only": True},
            "current_password": {"write_only": True},
            "new_password": {"write_only": True, "min_length": 8},
            "new_password_confirmation": {"write_only": True},
        }

    def validate(self, attrs):
        """
        Validate user input, including password confirmation and role assignment.
        """
        # Validate password confirmation on creation
        if self.context["request"].method == "POST":
            password = attrs.get("password")
            password_confirmation = attrs.get("password_confirmation")
            if not password_confirmation:
                raise serializers.ValidationError(
                    {"password_confirmation": "You must provide password confirmation."}
                )

            if password != password_confirmation:
                raise serializers.ValidationError({"password": "Passwords must match."})

        # Validate current password and new password on update
        if attrs.get("new_password") or attrs.get("new_password_confirmation"):
            current_password = attrs.get("current_password")
            new_password = attrs.get("new_password")
            new_password_confirmation = attrs.get("new_password_confirmation")

            if not current_password:
                raise serializers.ValidationError(
                    {
                        "current_password": "Current password is required to change password."
                    }
                )

            # Check current password if user is updating
            user = self.instance
            if not user or not user.check_password(current_password):
                raise serializers.ValidationError(
                    {"current_password": "Current password is incorrect."}
                )

            # Ensure new password and confirmation match
            if new_password != new_password_confirmation:
                raise serializers.ValidationError(
                    {"new_password": "New passwords must match."}
                )

        # Ensure user has only one role
        if attrs.get("is_teacher") and attrs.get("is_student"):
            raise serializers.ValidationError(
                "User cannot be both a teacher and a student"
            )

        return attrs

    def create(self, validated_data):
        """Create and return a user with encrypted password."""

        # Extract roles
        is_teacher = validated_data.pop("is_teacher", False)
        is_student = validated_data.pop("is_student", False)

        # Create user
        validated_data.pop("password_confirmation")
        password = validated_data.pop("password")
        user = get_user_model().objects.create_user(password=password, **validated_data)

        # Create associated role objects
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
        """Update the user and set the new password, if provided."""

        current_password = validated_data.pop("current_password", None)  # noqa
        new_password = validated_data.pop("new_password", None)
        validated_data.pop("new_password_confirmation", None)

        # Update user details
        user = super().update(instance, validated_data)

        # Set the new password if provided and valid
        if new_password:
            user.set_password(new_password)
            user.save()

        return user
