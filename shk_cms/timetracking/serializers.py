"""
Serializers for Time Tracking models
"""

from rest_framework import serializers
from django.utils import timezone
from .models import TimeEntry, Timesheet, WorkSchedule, OvertimeRequest
from shk_cms.employees.serializers import UserSerializer
from shk_cms.projects.serializers import ProjectSerializer
from shk_cms.customers.serializers import CustomerSerializer


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model"""
    
    employee_details = UserSerializer(source='employee', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'employee', 'employee_details', 'entry_type', 'entry_type_display',
            'date', 'start_time', 'end_time', 'duration_hours', 'duration_formatted',
            'project', 'project_details', 'customer', 'customer_details',
            'description', 'location', 'is_billable', 'is_approved', 'is_invoiced',
            'approved_by', 'approved_by_name', 'approved_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration_hours', 'duration_formatted', 'employee_details',
            'project_details', 'customer_details', 'entry_type_display',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at'
        ]


class TimesheetSerializer(serializers.ModelSerializer):
    """Serializer for Timesheet model"""
    
    employee_details = UserSerializer(source='employee', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    period_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Timesheet
        fields = [
            'id', 'employee', 'employee_details', 'start_date', 'end_date',
            'period_display', 'status', 'status_display', 'total_hours',
            'billable_hours', 'overtime_hours', 'submitted_date',
            'approved_by', 'approved_by_name', 'approved_date',
            'employee_notes', 'manager_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_hours', 'billable_hours', 'overtime_hours',
            'employee_details', 'status_display', 'approved_by', 'approved_by_name',
            'period_display', 'created_at', 'updated_at'
        ]


class TimesheetDetailSerializer(TimesheetSerializer):
    """Detailed Timesheet serializer with time entries"""
    
    time_entries = serializers.SerializerMethodField()
    entries_count = serializers.SerializerMethodField()
    
    class Meta(TimesheetSerializer.Meta):
        fields = TimesheetSerializer.Meta.fields + ['time_entries', 'entries_count']
    
    def get_time_entries(self, obj):
        """Get time entries for this timesheet period"""
        time_entries = TimeEntry.objects.filter(
            employee=obj.employee,
            date__gte=obj.start_date,
            date__lte=obj.end_date
        ).order_by('date', 'start_time')
        return TimeEntrySerializer(time_entries, many=True).data
    
    def get_entries_count(self, obj):
        """Get time entries count"""
        return TimeEntry.objects.filter(
            employee=obj.employee,
            date__gte=obj.start_date,
            date__lte=obj.end_date
        ).count()


class WorkScheduleSerializer(serializers.ModelSerializer):
    """Serializer for WorkSchedule model"""
    
    employee_details = UserSerializer(source='employee', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    schedule_type_display = serializers.CharField(source='get_schedule_type_display', read_only=True)
    planned_hours = serializers.ReadOnlyField()
    is_past_due = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'employee', 'employee_details', 'schedule_type', 'schedule_type_display',
            'date', 'start_time', 'end_time', 'break_duration', 'planned_hours',
            'project', 'project_details', 'location', 'notes', 'is_confirmed',
            'is_past_due', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'planned_hours', 'is_past_due', 'employee_details',
            'project_details', 'schedule_type_display', 'created_at', 'updated_at'
        ]


class OvertimeRequestSerializer(serializers.ModelSerializer):
    """Serializer for OvertimeRequest model"""
    
    employee_details = UserSerializer(source='employee', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = OvertimeRequest
        fields = [
            'id', 'employee', 'employee_details', 'date', 'planned_hours',
            'reason', 'project', 'project_details', 'status', 'status_display',
            'requested_date', 'approved_by', 'approved_by_name', 'approved_date',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_date', 'approved_by', 'approved_by_name',
            'employee_details', 'project_details', 'status_display',
            'created_at', 'updated_at'
        ]


class TimeTrackingStatsSerializer(serializers.Serializer):
    """Serializer for time tracking statistics"""
    
    total_hours_today = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_hours_week = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_hours_month = serializers.DecimalField(max_digits=6, decimal_places=2)
    billable_hours_week = serializers.DecimalField(max_digits=6, decimal_places=2)
    overtime_hours_month = serializers.DecimalField(max_digits=6, decimal_places=2)
    active_employees_today = serializers.IntegerField()
    pending_timesheets = serializers.IntegerField()
    pending_overtime_requests = serializers.IntegerField()


class TimeEntryBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating time entries"""
    
    time_entries = TimeEntrySerializer(many=True)
    
    def create(self, validated_data):
        """Create multiple time entries"""
        time_entries_data = validated_data['time_entries']
        time_entries = []
        
        for entry_data in time_entries_data:
            time_entry = TimeEntry.objects.create(**entry_data)
            time_entries.append(time_entry)
            
        return {'time_entries': time_entries}


class TimesheetApprovalSerializer(serializers.ModelSerializer):
    """Serializer for timesheet approval"""
    
    class Meta:
        model = Timesheet
        fields = ['status', 'manager_notes']
        
    def update(self, instance, validated_data):
        """Approve or reject timesheet"""
        status = validated_data.get('status')
        user = self.context['request'].user
        
        if status == 'approved':
            instance.approved_by = user
            instance.approved_date = timezone.now()
        elif status == 'rejected':
            instance.approved_by = None
            instance.approved_date = None
            
        instance.status = status
        instance.manager_notes = validated_data.get('manager_notes', instance.manager_notes)
        instance.save()
        
        return instance