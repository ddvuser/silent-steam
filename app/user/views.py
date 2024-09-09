"""
Views for the user API.
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from core.models import User, PasswordReset
from django.conf import settings
from core.utils import send_reset_pswd_link

from user.serializers import (
    UserSerializer,
    ResetPasswordSerializer,
    ResetPasswordRequestSerializer,
)
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator


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

    def put(self, request, *args, **kwargs):
        return Response(
            {"detail": "PUT method not allowed for this endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class RequestPasswordReset(generics.GenericAPIView):
    """Manage requesting password reset."""

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        self.serializer_class(data=request.data)
        email = request.data["email"]
        user = User.objects.filter(email__iexact=email).first()

        if user:
            link = PasswordReset.objects.filter(email=email).first()
            if link:
                # check if link has not expired
                if link.expires > timezone.now():
                    return Response({"warning": "We've already sent you a link."})
                # delete the link if expired
                else:
                    link.delete()
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(
                email=email, token=token, expires=timezone.now() + timedelta(minutes=5)
            )
            reset.save()

            reset_url = settings.APP_URL + f"api/user/reset-password/{token}"

            # send reset link using email
            send_reset_pswd_link(user, reset_url)

            return Response(
                {
                    "success": "We've sent you a link to reset your password. Expires in 5 minutes."
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User with provided creadentials not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResetPassword(generics.GenericAPIView):
    """Manage password resetting."""

    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        reset_obj = PasswordReset.objects.filter(token=token).first()

        # check if token exists
        if not reset_obj:
            return Response(
                {"error": "Token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if token expired
        if reset_obj.expires < timezone.now():
            reset_obj.delete()
            return Response(
                {"error": "Token has expired. Request for a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = data["new_password"]
        confirm_password = data["confirm_password"]

        if new_password != confirm_password:
            return Response(
                {"error": "New passwords must match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data["new_password"])
            user.save()

            reset_obj.delete()

            return Response({"success": "Password updated"})

        else:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
