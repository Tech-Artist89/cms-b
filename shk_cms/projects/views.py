"""
Views for Project models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import Project, ProjectTeamMember, ProjectTask, ProjectDocument
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    ProjectTeamMemberSerializer, ProjectTaskSerializer, ProjectDocumentSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project model"""
    
    queryset = Project.objects.select_related('customer', 'quote', 'project_manager').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project_type', 'status', 'customer', 'project_manager']
    search_fields = ['project_number', 'title', 'customer__customer_number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['start_date', 'end_date', 'deadline', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        """Filter projects based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's projects if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(project_manager=self.request.user) |
                Q(team_members=self.request.user) |
                Q(customer__sales_representative=self.request.user)
            ).distinct()
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get project statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_count': queryset.count(),
            'planning_count': queryset.filter(status='planning').count(),
            'in_progress_count': queryset.filter(status='in_progress').count(),
            'completed_count': queryset.filter(status='completed').count(),
            'on_hold_count': queryset.filter(status='on_hold').count(),
            'overdue_count': queryset.filter(
                deadline__lt=timezone.now().date(),
                status__in=['planning', 'approved', 'in_progress']
            ).count(),
            'avg_progress': queryset.aggregate(avg=Avg('progress_percentage'))['avg'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """Get projects assigned to current user"""
        queryset = self.get_queryset().filter(
            Q(project_manager=request.user) |
            Q(team_members=request.user)
        ).distinct()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue projects"""
        queryset = self.get_queryset().filter(
            deadline__lt=timezone.now().date(),
            status__in=['planning', 'approved', 'in_progress']
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Add task to project"""
        project = self.get_object()
        serializer = ProjectTaskSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get project tasks"""
        project = self.get_object()
        tasks = project.tasks.order_by('-priority', 'due_date')
        serializer = ProjectTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update project progress"""
        project = self.get_object()
        progress = request.data.get('progress_percentage')
        
        if progress is not None and 0 <= progress <= 100:
            project.progress_percentage = progress
            
            # Auto-update status based on progress
            if progress == 0:
                project.status = 'planning'
            elif progress == 100:
                project.status = 'completed'
            elif progress > 0:
                project.status = 'in_progress'
                
            project.save()
            
            serializer = self.get_serializer(project)
            return Response(serializer.data)
        
        return Response({'error': 'Invalid progress percentage'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class ProjectTeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectTeamMember model"""
    
    queryset = ProjectTeamMember.objects.select_related('project', 'user').all()
    serializer_class = ProjectTeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'user', 'role']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter team members based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's projects if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager=self.request.user) |
                Q(project__team_members=self.request.user) |
                Q(user=self.request.user)
            ).distinct()
            
        return queryset


class ProjectTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectTask model"""
    
    queryset = ProjectTask.objects.select_related('project', 'assigned_to', 'created_by').all()
    serializer_class = ProjectTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'status', 'priority', 'assigned_to', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-priority', 'due_date']
    
    def get_queryset(self):
        """Filter tasks based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's tasks if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager=self.request.user) |
                Q(project__team_members=self.request.user) |
                Q(assigned_to=self.request.user) |
                Q(created_by=self.request.user)
            ).distinct()
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        queryset = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        queryset = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_date = timezone.now()
        task.progress_percentage = 100
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class ProjectDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectDocument model"""
    
    queryset = ProjectDocument.objects.select_related('project', 'uploaded_by').all()
    serializer_class = ProjectDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'document_type', 'uploaded_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter documents based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's projects if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager=self.request.user) |
                Q(project__team_members=self.request.user) |
                Q(project__customer__sales_representative=self.request.user)
            ).distinct()
            
        return queryset