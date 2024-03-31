"""
Views for the user API.
"""

from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user API View."""

    serializer_class = UserSerializer
