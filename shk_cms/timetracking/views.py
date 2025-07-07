"""
Views for Time Tracking models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta

from .models import TimeEntry, Timesheet, WorkSchedule, OvertimeRequest
from .serializers import (
    TimeEntrySerializer, TimesheetSerializer, TimesheetDetailSerializer,
    WorkScheduleSerializer, OvertimeRequestSerializer, TimeTrackingStatsSerializer,
    TimeEntryBulkCreateSerializer, TimesheetApprovalSerializer
)


class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for TimeEntry model"""
    
    queryset = TimeEntry.objects.select_related('employee', 'project', 'customer', 'approved_by').all()
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'entry_type', 'project', 'customer', 'is_billable', 'is_approved']
    search_fields = ['description', 'location']
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['-date', 'start_time']
    
    def get_queryset(self):
        """Filter entries based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_entries(self, request):
        """Get current user's time entries"""
        queryset = self.get_queryset().filter(employee=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's time entries"""
        queryset = self.get_queryset().filter(date=date.today())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create time entries"""
        serializer = TimeEntryBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimesheetViewSet(viewsets.ModelViewSet):
    """ViewSet for Timesheet model"""
    
    queryset = Timesheet.objects.select_related('employee', 'approved_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status', 'approved_by']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TimesheetDetailSerializer
        elif self.action == 'approve':
            return TimesheetApprovalSerializer
        return TimesheetSerializer
    
    def get_queryset(self):
        """Filter timesheets based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get timesheets pending approval"""
        queryset = self.get_queryset().filter(status='submitted')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject timesheet"""
        timesheet = self.get_object()
        serializer = TimesheetApprovalSerializer(timesheet, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkSchedule model"""
    
    queryset = WorkSchedule.objects.select_related('employee', 'project').all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'schedule_type', 'project', 'is_confirmed']
    search_fields = ['location', 'notes']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    def get_queryset(self):
        """Filter schedules based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's work schedules"""
        queryset = self.get_queryset().filter(date=date.today())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def week(self, request):
        """Get current week's schedules"""
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        
        queryset = self.get_queryset().filter(date__range=[start_week, end_week])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OvertimeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for OvertimeRequest model"""
    
    queryset = OvertimeRequest.objects.select_related('employee', 'project', 'approved_by').all()
    serializer_class = OvertimeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status', 'project', 'approved_by']
    search_fields = ['reason']
    ordering_fields = ['date', 'requested_date']
    ordering = ['-requested_date']
    
    def get_queryset(self):
        """Filter requests based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending overtime requests"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)