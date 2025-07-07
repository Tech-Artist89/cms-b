"""
Views for Schedule models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from datetime import date, datetime, timedelta

from .models import Appointment, Calendar, CalendarPermission, RecurringAppointment, AppointmentNote
from .serializers import (
    AppointmentSerializer, AppointmentDetailSerializer, CalendarSerializer,
    CalendarPermissionSerializer, RecurringAppointmentSerializer, AppointmentNoteSerializer,
    ScheduleStatsSerializer, AppointmentBulkUpdateSerializer, CalendarViewSerializer
)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointment model"""
    
    queryset = Appointment.objects.select_related('customer', 'project', 'created_by').prefetch_related('assigned_employees').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['appointment_type', 'status', 'priority', 'customer', 'project', 'created_by']
    search_fields = ['title', 'description', 'customer__customer_number', 'location']
    ordering_fields = ['start_datetime', 'created_at', 'priority']
    ordering = ['start_datetime']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AppointmentDetailSerializer
        elif self.action == 'bulk_update':
            return AppointmentBulkUpdateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        """Filter appointments based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(assigned_employees=self.request.user) |
                Q(created_by=self.request.user) |
                Q(customer__sales_representative=self.request.user)
            ).distinct()
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = date.today()
        queryset = self.get_queryset().filter(start_datetime__date=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def week(self, request):
        """Get current week's appointments"""
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        
        queryset = self.get_queryset().filter(
            start_datetime__date__range=[start_week, end_week]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        """Get current user's appointments"""
        queryset = self.get_queryset().filter(
            Q(assigned_employees=request.user) |
            Q(created_by=request.user)
        ).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments (next 7 days)"""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            start_datetime__range=[start_date, end_date],
            status__in=['scheduled', 'confirmed']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update appointments"""
        serializer = AppointmentBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def calendar_view(self, request):
        """Get appointments for calendar view"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(
            start_datetime__date__range=[start_date, end_date]
        )
        
        calendar_data = {
            'start_date': start_date,
            'end_date': end_date,
            'appointments': self.get_serializer(queryset, many=True).data
        }
        
        serializer = CalendarViewSerializer(calendar_data)
        return Response(serializer.data)


class CalendarViewSet(viewsets.ModelViewSet):
    """ViewSet for Calendar model"""
    
    queryset = Calendar.objects.select_related('owner').all()
    serializer_class = CalendarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['calendar_type', 'owner', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter calendars based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(owner=self.request.user) |
                Q(is_public=True) |
                Q(shared_with=self.request.user)
            ).distinct()
        return queryset


class CalendarPermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for CalendarPermission model"""
    
    queryset = CalendarPermission.objects.select_related('calendar', 'user').all()
    serializer_class = CalendarPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['calendar', 'user', 'permission_level']
    ordering = ['-created_at']


class RecurringAppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for RecurringAppointment model"""
    
    queryset = RecurringAppointment.objects.select_related('customer', 'project', 'created_by').all()
    serializer_class = RecurringAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['recurrence_type', 'customer', 'project', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['start_date']
    
    @action(detail=True, methods=['post'])
    def generate_appointments(self, request, pk=None):
        """Generate appointments from recurring appointment"""
        recurring_appointment = self.get_object()
        end_date = request.data.get('end_date')
        
        if end_date:
            appointments = recurring_appointment.generate_appointments(end_date)
            return Response({
                'generated_count': len(appointments),
                'message': f'{len(appointments)} appointments generated'
            })
        
        return Response({'error': 'end_date required'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class AppointmentNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for AppointmentNote model"""
    
    queryset = AppointmentNote.objects.select_related('appointment', 'author').all()
    serializer_class = AppointmentNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['appointment', 'author', 'is_internal']
    search_fields = ['title', 'content']
    ordering = ['-created_at']