from rest_framework import serializers
from core.models import Assignment, Submission, Grade
from rest_framework.exceptions import PermissionDenied


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for assignment objects."""

    class Meta:
        model = Assignment
        fields = ["id", "class_assigned", "title", "description", "due_date"]

    def create(self, validated_data):
        # Ensure only teachers can create assignments
        request = self.context.get("request")
        if not hasattr(request.user, "teacher"):
            raise serializers.ValidationError(
                "You must be a teacher to create an assignment."
            )
        return super().create(validated_data)


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for submission objects."""

    class Meta:
        model = Submission
        fields = ["id", "assignment", "student", "submitted_date", "file"]

    def validate(self, data):
        # Ensure student is enrolled in the class of the assignment
        assignment = data["assignment"]
        student = data["student"]

        if not assignment.class_assigned.students.filter(id=student.id).exists():
            raise PermissionDenied(
                "You are not enrolled in the class for this assignment."
            )

        return data

    def create(self, validated_data):
        # Ensure only students can create submissions
        request = self.context.get("request")
        if not hasattr(request.user, "student"):
            raise PermissionDenied("You must be a student to submit an assignment.")
        return super().create(validated_data)


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for grade objects."""

    class Meta:
        model = Grade
        fields = ["id", "submission", "grade"]

    def create(self, validated_data):
        # Ensure only teachers can create grades
        request = self.context.get("request")
        if not hasattr(request.user, "teacher"):
            raise PermissionDenied("You must be a teacher to create a grade.")
        return super().create(validated_data)
