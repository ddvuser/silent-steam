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
        "token/",
        TokenObtainPairView.as_view(),
        name="obtain-token-pair",
    ),
    path(
        "token/refresh",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path("me/", views.ManageUserView.as_view(), name="me"),
    path(
        "request-password-reset/",
        views.RequestPasswordReset.as_view(),
        name="request-pass-reset",
    ),
    path(
        "reset-password/<str:token>/",
        views.ResetPassword.as_view(),
        name="reset-pass",
    ),
]
