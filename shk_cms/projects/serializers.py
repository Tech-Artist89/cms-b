"""
Serializers for Project models
"""

from rest_framework import serializers
from .models import Project, ProjectTeamMember, ProjectTask, ProjectDocument
from shk_cms.customers.serializers import CustomerSerializer
from shk_cms.quotes.serializers import QuoteSerializer


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectTeamMember model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = ProjectTeamMember
        fields = [
            'id', 'user', 'user_name', 'role', 'role_display',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'role_display', 'created_at', 'updated_at']


class ProjectTaskSerializer(serializers.ModelSerializer):
    """Serializer for ProjectTask model"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectTask
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'due_date', 'completed_date',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'progress_percentage', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_by_name', 'status_display', 
            'priority_display', 'assigned_to_name', 'is_overdue',
            'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDocument model"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'title', 
            'file', 'description', 'file_size', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'uploaded_by', 'uploaded_by_name', 
            'created_at', 'updated_at', 'document_type_display'
        ]
        
    def create(self, validated_data):
        """Set uploaded_by to current user"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    
    customer_details = CustomerSerializer(source='customer', read_only=True)
    quote_details = QuoteSerializer(source='quote', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    budget_utilization = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_number', 'customer', 'customer_details', 'quote', 'quote_details',
            'title', 'description', 'project_type', 'project_type_display', 
            'status', 'status_display', 'start_date', 'end_date', 'deadline',
            'budget_amount', 'actual_cost', 'budget_utilization', 'project_manager', 
            'project_manager_name', 'progress_percentage', 'is_overdue',
            'internal_notes', 'customer_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'project_number', 'customer_details', 'quote_details', 
            'status_display', 'project_type_display', 'project_manager_name',
            'is_overdue', 'budget_utilization', 'created_at', 'updated_at'
        ]


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed Project serializer with related data"""
    
    team_members = ProjectTeamMemberSerializer(source='projectteammember_set', many=True, read_only=True)
    tasks = ProjectTaskSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    
    # Statistics
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    open_tasks_count = serializers.SerializerMethodField()
    overdue_tasks_count = serializers.SerializerMethodField()
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            'team_members', 'tasks', 'documents',
            'tasks_count', 'completed_tasks_count', 'open_tasks_count', 'overdue_tasks_count'
        ]
    
    def get_tasks_count(self, obj):
        """Get total tasks count"""
        return obj.tasks.count()
    
    def get_completed_tasks_count(self, obj):
        """Get completed tasks count"""
        return obj.tasks.filter(status='completed').count()
    
    def get_open_tasks_count(self, obj):
        """Get open tasks count"""
        return obj.tasks.filter(status__in=['pending', 'in_progress']).count()
    
    def get_overdue_tasks_count(self, obj):
        """Get overdue tasks count"""
        from datetime import datetime
        return obj.tasks.filter(
            due_date__lt=datetime.now(),
            status__in=['pending', 'in_progress']
        ).count()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating projects with team members"""
    
    team_members = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Project
        fields = [
            'customer', 'quote', 'title', 'description', 'project_type',
            'status', 'start_date', 'end_date', 'deadline', 'budget_amount',
            'project_manager', 'progress_percentage', 'internal_notes',
            'customer_notes', 'team_members'
        ]
        
    def create(self, validated_data):
        """Create project with team members"""
        team_members_ids = validated_data.pop('team_members', [])
        
        project = Project.objects.create(**validated_data)
        
        # Add team members
        for user_id in team_members_ids:
            ProjectTeamMember.objects.create(
                project=project,
                user_id=user_id,
                role='technician'  # Default role
            )
            
        return project
        
    def update(self, instance, validated_data):
        """Update project and team members"""
        team_members_ids = validated_data.pop('team_members', None)
        
        # Update project fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update team members if provided
        if team_members_ids is not None:
            # Remove existing team members
            instance.projectteammember_set.all().delete()
            
            # Add new team members
            for user_id in team_members_ids:
                ProjectTeamMember.objects.create(
                    project=instance,
                    user_id=user_id,
                    role='technician'  # Default role
                )
                
        return instance