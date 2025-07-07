"""
URL configuration for Time Tracking app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeEntryViewSet, TimesheetViewSet, WorkScheduleViewSet, OvertimeRequestViewSet

app_name = 'timetracking'

router = DefaultRouter()
router.register(r'entries', TimeEntryViewSet)
router.register(r'timesheets', TimesheetViewSet)
router.register(r'schedules', WorkScheduleViewSet)
router.register(r'overtime-requests', OvertimeRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]