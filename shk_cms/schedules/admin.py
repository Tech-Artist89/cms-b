"""
Django Admin configuration for Schedule models
"""

from django.contrib import admin
from .models import Appointment, Calendar, CalendarPermission, RecurringAppointment, AppointmentNote


class AppointmentNoteInline(admin.TabularInline):
    model = AppointmentNote
    extra = 0
    readonly_fields = ['author']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'start_datetime', 'end_datetime', 'appointment_type', 'status', 'priority', 'is_today']
    list_filter = ['appointment_type', 'status', 'priority', 'start_datetime', 'created_by']
    search_fields = ['title', 'customer__customer_number', 'customer__first_name', 'customer__last_name', 'description']
    ordering = ['start_datetime']
    readonly_fields = ['duration_hours', 'is_past_due', 'is_today', 'created_at', 'updated_at']
    
    inlines = [AppointmentNoteInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('title', 'appointment_type', 'status', 'priority')
        }),
        ('Zeitplanung', {
            'fields': ('start_datetime', 'end_datetime', 'duration_hours')
        }),
        ('Verknüpfungen', {
            'fields': ('customer', 'project')
        }),
        ('Zuweisungen', {
            'fields': ('assigned_employees', 'created_by')
        }),
        ('Lokation', {
            'fields': ('location',)
        }),
        ('Fahrtzeiten', {
            'fields': ('travel_time_to', 'travel_time_from'),
            'classes': ('collapse',)
        }),
        ('Beschreibung', {
            'fields': ('description',)
        }),
        ('Erinnerungen', {
            'fields': ('reminder_sent', 'reminder_datetime'),
            'classes': ('collapse',)
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


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ['name', 'calendar_type', 'owner', 'color', 'is_active', 'is_public']
    list_filter = ['calendar_type', 'is_active', 'is_public', 'owner']
    search_fields = ['name', 'description', 'owner__first_name', 'owner__last_name']
    ordering = ['name']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('name', 'description', 'calendar_type', 'owner')
        }),
        ('Darstellung', {
            'fields': ('color',)
        }),
        ('Zugriff', {
            'fields': ('is_active', 'is_public')
        })
    )


@admin.register(CalendarPermission)
class CalendarPermissionAdmin(admin.ModelAdmin):
    list_display = ['calendar', 'user', 'permission_level', 'created_at']
    list_filter = ['permission_level', 'calendar__calendar_type', 'created_at']
    search_fields = ['calendar__name', 'user__first_name', 'user__last_name']
    ordering = ['calendar__name', 'user__last_name']


@admin.register(RecurringAppointment)
class RecurringAppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'recurrence_type', 'interval', 'start_date', 'end_date', 'is_active']
    list_filter = ['recurrence_type', 'appointment_type', 'is_active', 'start_date']
    search_fields = ['title', 'customer__customer_number', 'customer__first_name', 'customer__last_name']
    ordering = ['start_date', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('title', 'appointment_type', 'customer', 'project')
        }),
        ('Wiederholung', {
            'fields': ('recurrence_type', 'interval', 'start_date', 'end_date', 'is_active')
        }),
        ('Zeitplanung', {
            'fields': ('start_time', 'duration_hours')
        }),
        ('Zuweisungen', {
            'fields': ('assigned_employees', 'created_by')
        }),
        ('Details', {
            'fields': ('description', 'location', 'internal_notes')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AppointmentNote)
class AppointmentNoteAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'title', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'author', 'created_at']
    search_fields = ['appointment__title', 'title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['author', 'created_at', 'updated_at']