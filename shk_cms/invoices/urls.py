"""
URL configuration for Invoices app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceItemViewSet, PaymentViewSet, ReminderViewSet

app_name = 'invoices'

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'items', InvoiceItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reminders', ReminderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]