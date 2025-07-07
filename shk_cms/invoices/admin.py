"""
Django Admin configuration for Invoice models
"""

from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment, Reminder


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total_price']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['recorded_by']


class ReminderInline(admin.TabularInline):
    model = Reminder
    extra = 0
    readonly_fields = ['created_by']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_type', 'status', 'total_amount', 'invoice_date', 'due_date', 'outstanding_amount']
    list_filter = ['invoice_type', 'status', 'invoice_date', 'due_date', 'created_by']
    search_fields = ['invoice_number', 'customer__customer_number', 'customer__first_name', 'customer__last_name', 'title']
    ordering = ['-invoice_date', '-invoice_number']
    readonly_fields = ['invoice_number', 'subtotal', 'tax_amount', 'total_amount', 'paid_amount', 'outstanding_amount', 'created_at', 'updated_at']
    
    inlines = [InvoiceItemInline, PaymentInline, ReminderInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('invoice_number', 'customer', 'project', 'invoice_type', 'status')
        }),
        ('Rechnungsdaten', {
            'fields': ('title', 'description', 'invoice_date', 'due_date', 'payment_date')
        }),
        ('Beträge', {
            'fields': ('discount_percent', 'tax_rate', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount', 'paid_amount'),
            'classes': ('collapse',)
        }),
        ('Texte', {
            'fields': ('payment_terms', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Zahlungsreferenz', {
            'fields': ('payment_reference',),
            'classes': ('collapse',)
        }),
        ('Zuweisungen', {
            'fields': ('created_by',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'position_number', 'title', 'quantity', 'unit_price', 'total_price', 'item_type']
    list_filter = ['item_type', 'invoice__invoice_date']
    search_fields = ['invoice__invoice_number', 'title', 'description', 'item_number']
    ordering = ['invoice__invoice_number', 'position_number']
    readonly_fields = ['total_price']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_date', 'payment_method', 'recorded_by']
    list_filter = ['payment_method', 'payment_date', 'recorded_by']
    search_fields = ['invoice__invoice_number', 'reference_number', 'bank_reference']
    ordering = ['-payment_date']
    readonly_fields = ['recorded_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('invoice', 'amount', 'payment_date', 'payment_method')
        }),
        ('Referenzen', {
            'fields': ('reference_number', 'bank_reference'),
            'classes': ('collapse',)
        }),
        ('Zusätzliche Informationen', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Verwaltung', {
            'fields': ('recorded_by',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'reminder_level', 'reminder_date', 'reminder_fee', 'is_sent', 'sent_date']
    list_filter = ['reminder_level', 'is_sent', 'reminder_date', 'created_by']
    search_fields = ['invoice__invoice_number', 'reminder_text']
    ordering = ['-reminder_date', '-reminder_level']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('invoice', 'reminder_level', 'reminder_date', 'reminder_fee')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_date')
        }),
        ('Inhalt', {
            'fields': ('reminder_text',),
            'classes': ('collapse',)
        }),
        ('Verwaltung', {
            'fields': ('created_by',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )