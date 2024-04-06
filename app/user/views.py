"""
Views for the user API.
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user API View."""

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        is_teacher = request.data.get("is_teacher", False)
        is_student = request.data.get("is_student", False)

        if is_teacher and is_student:
            return Response(
                {"error": "User cannot be both a teacher and a student."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not is_teacher and not is_student:
            return Response(
                {"error": "You must choose between student and teacher."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().post(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
