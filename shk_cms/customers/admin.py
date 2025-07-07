"""
Django Admin configuration for Customer models
"""

from django.contrib import admin
from .models import Customer, CustomerAddress, CustomerContact, CustomerInteraction


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_number', 'display_name', 'customer_type', 'category', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['customer_type', 'category', 'is_active', 'is_blocked', 'created_at']
    search_fields = ['customer_number', 'first_name', 'last_name', 'email', 'phone', 'company__name']
    ordering = ['customer_number']
    readonly_fields = ['customer_number', 'created_at', 'updated_at']
    
    inlines = [CustomerAddressInline, CustomerContactInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('customer_number', 'customer_type', 'category')
        }),
        ('Privatkunde', {
            'fields': ('salutation', 'first_name', 'last_name', 'title'),
            'classes': ('collapse',)
        }),
        ('Geschäftskunde', {
            'fields': ('company',),
            'classes': ('collapse',)
        }),
        ('Kontaktdaten', {
            'fields': ('email', 'phone', 'mobile', 'fax')
        }),
        ('Steuerliche Informationen', {
            'fields': ('tax_number', 'vat_number'),
            'classes': ('collapse',)
        }),
        ('Zahlungskonditionen', {
            'fields': ('payment_terms_days', 'discount_percent'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_blocked', 'sales_representative')
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


@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'interaction_type', 'subject', 'interaction_date', 'employee', 'follow_up_required']
    list_filter = ['interaction_type', 'follow_up_required', 'interaction_date', 'employee']
    search_fields = ['customer__customer_number', 'customer__first_name', 'customer__last_name', 'subject', 'content']
    ordering = ['-interaction_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('customer', 'interaction_type', 'subject', 'interaction_date', 'employee')
        }),
        ('Inhalt', {
            'fields': ('content',)
        }),
        ('Nachverfolgung', {
            'fields': ('follow_up_required', 'follow_up_date'),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )