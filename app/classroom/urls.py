"""
URL mappings for the classroom app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from classroom import views

router = DefaultRouter()
router.register("classroom", views.ClassroomViewSet, basename="classroom")

app_name = "classroom"

urlpatterns = [
    path("", include(router.urls)),
]
