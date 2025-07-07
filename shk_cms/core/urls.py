"""
URL configuration for Core app (Authentication & Core Models)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import AddressViewSet, ContactPersonViewSet, CompanyViewSet, NoteViewSet

app_name = 'core'

# API Router for core models
router = DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactPersonViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'notes', NoteViewSet)

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Core model endpoints
    path('', include(router.urls)),
]