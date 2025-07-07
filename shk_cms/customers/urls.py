"""
URL configuration for Customers app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerAddressViewSet, CustomerContactViewSet, CustomerInteractionViewSet

app_name = 'customers'

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'addresses', CustomerAddressViewSet)
router.register(r'contacts', CustomerContactViewSet)
router.register(r'interactions', CustomerInteractionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]