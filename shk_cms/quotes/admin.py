"""
Django Admin configuration for Quote models
"""

from django.contrib import admin
from .models import Quote, QuoteItem, QuoteDocument


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    readonly_fields = ['total_price']


class QuoteDocumentInline(admin.TabularInline):
    model = QuoteDocument
    extra = 0
    readonly_fields = ['file_size', 'uploaded_by']


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'customer', 'title', 'status', 'total_amount', 'quote_date', 'valid_until']
    list_filter = ['status', 'quote_date', 'valid_until', 'created_by']
    search_fields = ['quote_number', 'customer__customer_number', 'customer__first_name', 'customer__last_name', 'title']
    ordering = ['-quote_date', '-quote_number']
    readonly_fields = ['quote_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at']
    
    inlines = [QuoteItemInline, QuoteDocumentInline]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('quote_number', 'customer', 'status', 'version')
        }),
        ('Angebotsdaten', {
            'fields': ('title', 'description', 'quote_date', 'valid_until')
        }),
        ('Beträge', {
            'fields': ('discount_percent', 'tax_rate', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Texte', {
            'fields': ('terms_and_conditions', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Zuweisungen', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ['quote', 'position_number', 'title', 'quantity', 'unit_price', 'total_price', 'item_type']
    list_filter = ['item_type', 'quote__quote_date']
    search_fields = ['quote__quote_number', 'title', 'description', 'item_number']
    ordering = ['quote__quote_number', 'position_number']
    readonly_fields = ['total_price']


@admin.register(QuoteDocument)
class QuoteDocumentAdmin(admin.ModelAdmin):
    list_display = ['quote', 'title', 'document_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'uploaded_by', 'created_at']
    search_fields = ['quote__quote_number', 'title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['file_size', 'uploaded_by', 'created_at', 'updated_at']