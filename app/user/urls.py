"""
URL mappings for the user API.
"""

from django.urls import path

from user import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="obtain-token-pair",
    ),
    path(
        "api/token/refresh",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path("api/me/", views.ManageUserView.as_view(), name="me"),
]
