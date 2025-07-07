"""
URL configuration for Schedules app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, CalendarViewSet, CalendarPermissionViewSet, RecurringAppointmentViewSet, AppointmentNoteViewSet

app_name = 'schedules'

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'calendars', CalendarViewSet)
router.register(r'permissions', CalendarPermissionViewSet)
router.register(r'recurring', RecurringAppointmentViewSet)
router.register(r'notes', AppointmentNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]