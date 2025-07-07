"""
URL configuration for Projects app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectTeamMemberViewSet, ProjectTaskViewSet, ProjectDocumentViewSet

app_name = 'projects'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'team-members', ProjectTeamMemberViewSet)
router.register(r'tasks', ProjectTaskViewSet)
router.register(r'documents', ProjectDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]