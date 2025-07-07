"""
Views for Employee models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from django.db.models import Count, Avg

from .models import Employee, EmployeeSkill, EmployeeDocument, EmployeeAvailability
from .serializers import (
    EmployeeSerializer, EmployeeDetailSerializer, EmployeeCreateUpdateSerializer,
    EmployeeSkillSerializer, EmployeeDocumentSerializer, EmployeeAvailabilitySerializer,
    UserSerializer, EmployeeStatsSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User model (read-only)"""
    
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee model"""
    
    queryset = Employee.objects.select_related('user', 'address', 'supervisor').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employment_status', 'employment_type', 'department', 'supervisor']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'position']
    ordering_fields = ['employee_number', 'hire_date', 'user__last_name']
    ordering = ['employee_number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        queryset = self.get_queryset()
        departments = queryset.values('department').annotate(count=Count('id'))
        
        stats_data = {
            'total_count': queryset.count(),
            'active_count': queryset.filter(employment_status='active').count(),
            'inactive_count': queryset.filter(employment_status='inactive').count(),
            'on_vacation_count': queryset.filter(employment_status='vacation').count(),
            'sick_count': queryset.filter(employment_status='sick').count(),
            'departments': {dept['department']: dept['count'] for dept in departments if dept['department']},
            'avg_weekly_hours': queryset.aggregate(avg=Avg('weekly_hours'))['avg'] or 0,
        }
        return Response(stats_data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active employees"""
        queryset = self.get_queryset().filter(employment_status='active')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeeSkill model"""
    
    queryset = EmployeeSkill.objects.select_related('employee').all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'category', 'level']
    search_fields = ['name', 'certification_body']
    ordering = ['employee__employee_number', 'category', 'name']


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeeDocument model"""
    
    queryset = EmployeeDocument.objects.select_related('employee', 'uploaded_by').all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'document_type', 'uploaded_by']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


class EmployeeAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeeAvailability model"""
    
    queryset = EmployeeAvailability.objects.select_related('employee', 'approved_by').all()
    serializer_class = EmployeeAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'availability_type', 'is_approved']
    ordering = ['-start_date']
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get availability requests pending approval"""
        queryset = self.get_queryset().filter(is_approved=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)