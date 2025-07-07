"""
Django Admin configuration for Core models
"""

from django.contrib import admin
from .models import Address, ContactPerson, Company, Note


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'street_number', 'postal_code', 'city', 'type', 'created_at']
    list_filter = ['type', 'country', 'created_at']
    search_fields = ['street', 'city', 'postal_code']
    ordering = ['city', 'street']


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'position', 'is_primary', 'created_at']
    list_filter = ['salutation', 'is_primary', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering = ['last_name', 'first_name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_form', 'email', 'phone', 'is_own_company', 'created_at']
    list_filter = ['legal_form', 'is_own_company', 'created_at']
    search_fields = ['name', 'email', 'tax_number', 'vat_number']
    ordering = ['name']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_type', 'author', 'created_at']
    list_filter = ['note_type', 'author', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']