"""
URL configuration for Employees app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EmployeeViewSet, EmployeeSkillViewSet, EmployeeDocumentViewSet, EmployeeAvailabilityViewSet

app_name = 'employees'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'skills', EmployeeSkillViewSet)
router.register(r'documents', EmployeeDocumentViewSet)
router.register(r'availability', EmployeeAvailabilityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]