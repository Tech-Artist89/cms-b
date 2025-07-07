"""
Serializers for Schedule models
"""

from rest_framework import serializers
from .models import Appointment, Calendar, CalendarPermission, RecurringAppointment, AppointmentNote
from shk_cms.customers.serializers import CustomerSerializer
from shk_cms.projects.serializers import ProjectSerializer
from shk_cms.employees.serializers import UserSerializer


class AppointmentNoteSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentNote model"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = AppointmentNote
        fields = [
            'id', 'title', 'content', 'author', 'author_name', 
            'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        """Set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    
    customer_details = CustomerSerializer(source='customer', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    assigned_employees_details = UserSerializer(source='assigned_employees', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    is_past_due = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'title', 'description', 'appointment_type', 'appointment_type_display',
            'status', 'status_display', 'priority', 'priority_display',
            'start_datetime', 'end_datetime', 'duration_hours', 'duration_formatted',
            'customer', 'customer_details', 'project', 'project_details',
            'assigned_employees', 'assigned_employees_details', 'created_by', 'created_by_name',
            'location', 'reminder_sent', 'reminder_datetime', 'internal_notes',
            'customer_notes', 'travel_time_to', 'travel_time_from',
            'is_past_due', 'is_today', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration_hours', 'duration_formatted', 'customer_details',
            'project_details', 'assigned_employees_details', 'created_by', 'created_by_name',
            'appointment_type_display', 'status_display', 'priority_display',
            'is_past_due', 'is_today', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentDetailSerializer(AppointmentSerializer):
    """Detailed Appointment serializer with notes"""
    
    notes = AppointmentNoteSerializer(many=True, read_only=True)
    notes_count = serializers.SerializerMethodField()
    
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ['notes', 'notes_count']
    
    def get_notes_count(self, obj):
        """Get notes count"""
        return obj.notes.count()


class CalendarPermissionSerializer(serializers.ModelSerializer):
    """Serializer for CalendarPermission model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    permission_level_display = serializers.CharField(source='get_permission_level_display', read_only=True)
    
    class Meta:
        model = CalendarPermission
        fields = [
            'id', 'user', 'user_name', 'permission_level', 'permission_level_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'permission_level_display', 'created_at', 'updated_at']


class CalendarSerializer(serializers.ModelSerializer):
    """Serializer for Calendar model"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    calendar_type_display = serializers.CharField(source='get_calendar_type_display', read_only=True)
    permissions = CalendarPermissionSerializer(source='calendarpermission_set', many=True, read_only=True)
    
    class Meta:
        model = Calendar
        fields = [
            'id', 'name', 'description', 'calendar_type', 'calendar_type_display',
            'color', 'owner', 'owner_name', 'is_active', 'is_public',
            'permissions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner_name', 'calendar_type_display', 'permissions',
            'created_at', 'updated_at'
        ]


class RecurringAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for RecurringAppointment model"""
    
    customer_details = CustomerSerializer(source='customer', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    assigned_employees_details = UserSerializer(source='assigned_employees', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    recurrence_type_display = serializers.CharField(source='get_recurrence_type_display', read_only=True)
    
    class Meta:
        model = RecurringAppointment
        fields = [
            'id', 'title', 'description', 'appointment_type', 'appointment_type_display',
            'customer', 'customer_details', 'project', 'project_details',
            'recurrence_type', 'recurrence_type_display', 'interval',
            'start_time', 'duration_hours', 'start_date', 'end_date',
            'assigned_employees', 'assigned_employees_details', 'created_by', 'created_by_name',
            'is_active', 'location', 'internal_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_details', 'project_details', 'assigned_employees_details',
            'created_by', 'created_by_name', 'appointment_type_display',
            'recurrence_type_display', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ScheduleStatsSerializer(serializers.Serializer):
    """Serializer for schedule statistics"""
    
    appointments_today = serializers.IntegerField()
    appointments_week = serializers.IntegerField()
    appointments_month = serializers.IntegerField()
    confirmed_today = serializers.IntegerField()
    pending_today = serializers.IntegerField()
    overdue_appointments = serializers.IntegerField()
    active_calendars = serializers.IntegerField()
    recurring_appointments = serializers.IntegerField()


class AppointmentBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating appointments"""
    
    appointment_ids = serializers.ListField(child=serializers.UUIDField())
    status = serializers.ChoiceField(choices=Appointment.APPOINTMENT_STATUS, required=False)
    assigned_employees = serializers.ListField(child=serializers.UUIDField(), required=False)
    
    def update(self, instance, validated_data):
        """Bulk update appointments"""
        appointment_ids = validated_data['appointment_ids']
        appointments = Appointment.objects.filter(id__in=appointment_ids)
        
        updates = {}
        if 'status' in validated_data:
            updates['status'] = validated_data['status']
            
        if updates:
            appointments.update(**updates)
            
        if 'assigned_employees' in validated_data:
            for appointment in appointments:
                appointment.assigned_employees.set(validated_data['assigned_employees'])
                
        return {'updated_count': appointments.count()}


class CalendarViewSerializer(serializers.Serializer):
    """Serializer for calendar view with appointments"""
    
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    appointments = AppointmentSerializer(many=True, read_only=True)
    
    def to_representation(self, instance):
        """Custom representation for calendar view"""
        data = super().to_representation(instance)
        
        # Group appointments by date
        appointments_by_date = {}
        for appointment in data['appointments']:
            date = appointment['start_datetime'][:10]  # Get date part
            if date not in appointments_by_date:
                appointments_by_date[date] = []
            appointments_by_date[date].append(appointment)
            
        data['appointments_by_date'] = appointments_by_date
        return data