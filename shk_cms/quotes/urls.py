"""
URL configuration for Quotes app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteViewSet, QuoteItemViewSet, QuoteDocumentViewSet

app_name = 'quotes'

router = DefaultRouter()
router.register(r'quotes', QuoteViewSet)
router.register(r'items', QuoteItemViewSet)
router.register(r'documents', QuoteDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]