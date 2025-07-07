"""
Serializers for Core models
"""

from rest_framework import serializers
from .models import Address, ContactPerson, Company, Note


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Address
        fields = [
            'id', 'type', 'street', 'street_number', 'postal_code', 'city', 
            'country', 'address_line_2', 'state', 'full_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_address']


class ContactPersonSerializer(serializers.ModelSerializer):
    """Serializer for ContactPerson model"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactPerson
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'title', 'position',
            'email', 'phone', 'mobile', 'notes', 'is_primary', 'full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'legal_form', 'trade_register_number', 'tax_number', 
            'vat_number', 'email', 'phone', 'fax', 'website', 'bank_name', 
            'iban', 'bic', 'logo', 'notes', 'is_own_company',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'note_type', 'content_type', 'object_id',
            'author', 'author_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author_name']
        
    def create(self, validated_data):
        """Set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)