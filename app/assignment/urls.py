"""
URL mappings for the assignment app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from assignment import views

router = DefaultRouter()
router.register("assignment", views.AssignmentViewSet, basename="assignment")
router.register("submission", views.SubmissionViewSet, basename="submission")
router.register("grade", views.GradeViewSet, basename="grade")

app_name = "assignment"

urlpatterns = [
    path("", include(router.urls)),
]
