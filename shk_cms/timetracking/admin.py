"""
Django Admin configuration for Time Tracking models
"""

from django.contrib import admin
from .models import TimeEntry, Timesheet, WorkSchedule, OvertimeRequest


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'start_time', 'end_time', 'duration_hours', 'entry_type', 'project', 'is_billable', 'is_approved']
    list_filter = ['entry_type', 'date', 'is_billable', 'is_approved', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'project__project_number', 'description']
    ordering = ['-date', 'employee']
    readonly_fields = ['duration_hours', 'approved_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'entry_type', 'date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Projektbezug', {
            'fields': ('project', 'customer', 'location')
        }),
        ('Details', {
            'fields': ('description', 'notes')
        }),
        ('Status', {
            'fields': ('is_billable', 'is_approved', 'is_invoiced', 'approved_by', 'approved_date')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'status', 'total_hours', 'billable_hours', 'overtime_hours']
    list_filter = ['status', 'start_date', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-start_date', 'employee']
    readonly_fields = ['total_hours', 'billable_hours', 'overtime_hours', 'approved_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'start_date', 'end_date', 'status')
        }),
        ('Stundenübersicht', {
            'fields': ('total_hours', 'billable_hours', 'overtime_hours')
        }),
        ('Bearbeitung', {
            'fields': ('submitted_date', 'approved_by', 'approved_date')
        }),
        ('Notizen', {
            'fields': ('employee_notes', 'manager_notes'),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'start_time', 'end_time', 'planned_hours', 'schedule_type', 'project', 'is_confirmed']
    list_filter = ['schedule_type', 'date', 'is_confirmed']
    search_fields = ['employee__first_name', 'employee__last_name', 'project__project_number', 'location']
    ordering = ['date', 'start_time', 'employee']
    readonly_fields = ['planned_hours', 'is_past_due', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'schedule_type', 'date', 'start_time', 'end_time', 'break_duration')
        }),
        ('Projektbezug', {
            'fields': ('project', 'location')
        }),
        ('Status', {
            'fields': ('is_confirmed',)
        }),
        ('Notizen', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'planned_hours', 'status', 'project', 'requested_date', 'approved_by']
    list_filter = ['status', 'date', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'project__project_number', 'reason']
    ordering = ['-requested_date']
    readonly_fields = ['requested_date', 'approved_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'date', 'planned_hours', 'status')
        }),
        ('Details', {
            'fields': ('reason', 'project')
        }),
        ('Bearbeitung', {
            'fields': ('requested_date', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )