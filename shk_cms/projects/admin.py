"""
Django Admin configuration for Project models
"""

from django.contrib import admin
from .models import Project, ProjectTeamMember, ProjectTask, ProjectDocument


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 0


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0
    readonly_fields = ['created_by']


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0
    readonly_fields = ['file_size', 'uploaded_by']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_number', 'title', 'customer', 'project_type', 'status', 'start_date', 'end_date', 'progress_percentage']
    list_filter = ['project_type', 'status', 'start_date', 'end_date', 'project_manager']
    search_fields = ['project_number', 'title', 'customer__customer_number', 'customer__first_name', 'customer__last_name']
    ordering = ['-created_at']
    readonly_fields = ['project_number', 'created_at', 'updated_at']
    
    inlines = [ProjectTeamMemberInline, ProjectTaskInline, ProjectDocumentInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('project_number', 'customer', 'quote', 'title', 'project_type', 'status')
        }),
        ('Projektdetails', {
            'fields': ('description', 'start_date', 'end_date', 'deadline', 'progress_percentage')
        }),
        ('Budget', {
            'fields': ('budget_amount', 'actual_cost'),
            'classes': ('collapse',)
        }),
        ('Zuweisungen', {
            'fields': ('project_manager',)
        }),
        ('Notizen', {
            'fields': ('internal_notes', 'customer_notes'),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'status', 'priority', 'assigned_to', 'due_date', 'progress_percentage']
    list_filter = ['status', 'priority', 'assigned_to', 'due_date', 'created_by']
    search_fields = ['project__project_number', 'title', 'description']
    ordering = ['-priority', 'due_date']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('project', 'title', 'status', 'priority')
        }),
        ('Details', {
            'fields': ('description', 'due_date', 'completed_date', 'progress_percentage')
        }),
        ('Zuweisungen', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'document_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'uploaded_by', 'created_at']
    search_fields = ['project__project_number', 'title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['file_size', 'uploaded_by', 'created_at', 'updated_at']