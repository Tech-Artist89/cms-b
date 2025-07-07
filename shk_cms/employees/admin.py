"""
Django Admin configuration for Employee models
"""

from django.contrib import admin
from .models import Employee, EmployeeSkill, EmployeeDocument, EmployeeAvailability


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 0


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0
    readonly_fields = ['file_size', 'uploaded_by']


class EmployeeAvailabilityInline(admin.TabularInline):
    model = EmployeeAvailability
    extra = 0
    readonly_fields = ['approved_by']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'full_name', 'employment_status', 'employment_type', 'department', 'position', 'hire_date']
    list_filter = ['employment_status', 'employment_type', 'department', 'hire_date', 'supervisor']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'user__email', 'position', 'department']
    ordering = ['employee_number']
    readonly_fields = ['employee_number', 'created_at', 'updated_at']
    
    inlines = [EmployeeSkillInline, EmployeeDocumentInline, EmployeeAvailabilityInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee_number', 'user', 'employment_status', 'employment_type')
        }),
        ('Persönliche Daten', {
            'fields': ('birth_date', 'phone_private', 'phone_business', 'mobile', 'address')
        }),
        ('Arbeitsplatz', {
            'fields': ('department', 'position', 'supervisor')
        }),
        ('Beschäftigung', {
            'fields': ('hire_date', 'termination_date', 'weekly_hours', 'hourly_rate')
        }),
        ('Qualifikationen', {
            'fields': ('qualifications', 'certifications'),
            'classes': ('collapse',)
        }),
        ('Notfallkontakt', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
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


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ['employee', 'name', 'category', 'level', 'acquired_date', 'expiry_date', 'is_expired']
    list_filter = ['category', 'level', 'acquired_date', 'expiry_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'name', 'certification_body']
    ordering = ['employee__employee_number', 'category', 'name']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'name', 'category', 'level')
        }),
        ('Details', {
            'fields': ('description', 'acquired_date', 'expiry_date')
        }),
        ('Zertifizierung', {
            'fields': ('certification_body', 'certificate_number'),
            'classes': ('collapse',)
        })
    )


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'document_type', 'issue_date', 'expiry_date', 'is_expired', 'uploaded_by']
    list_filter = ['document_type', 'issue_date', 'expiry_date', 'uploaded_by']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['file_size', 'uploaded_by', 'created_at', 'updated_at']


@admin.register(EmployeeAvailability)
class EmployeeAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['employee', 'availability_type', 'start_date', 'end_date', 'duration_days', 'is_approved', 'is_current']
    list_filter = ['availability_type', 'is_approved', 'start_date', 'approved_by']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    ordering = ['-start_date']
    readonly_fields = ['approved_by', 'duration_days', 'is_current', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('employee', 'availability_type', 'start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('reason', 'notes')
        }),
        ('Genehmigung', {
            'fields': ('is_approved', 'approved_by', 'approved_date'),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )