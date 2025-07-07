"""
Serializers for Customer models
"""

from rest_framework import serializers
from .models import Customer, CustomerAddress, CustomerContact, CustomerInteraction
from shk_cms.core.serializers import AddressSerializer, ContactPersonSerializer, CompanySerializer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    
    display_name = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    company_details = CompanySerializer(source='company', read_only=True)
    sales_representative_name = serializers.CharField(
        source='sales_representative.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_number', 'customer_type', 'category',
            'salutation', 'first_name', 'last_name', 'title',
            'company', 'company_details', 'email', 'phone', 'mobile', 'fax',
            'tax_number', 'vat_number', 'payment_terms_days', 'discount_percent',
            'is_active', 'is_blocked', 'notes', 'sales_representative',
            'sales_representative_name', 'display_name', 'full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_number', 'created_at', 'updated_at', 
            'display_name', 'full_name', 'company_details', 'sales_representative_name'
        ]
        
    def validate(self, data):
        """Validate customer data based on type"""
        customer_type = data.get('customer_type', 'private')
        
        if customer_type == 'private':
            if not data.get('first_name') or not data.get('last_name'):
                raise serializers.ValidationError(
                    "Vor- und Nachname sind für Privatkunden erforderlich."
                )
        elif customer_type == 'business':
            if not data.get('company'):
                raise serializers.ValidationError(
                    "Firma ist für Geschäftskunden erforderlich."
                )
                
        return data


class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer for CustomerAddress model"""
    
    address_details = AddressSerializer(source='address', read_only=True)
    customer_name = serializers.CharField(source='customer.display_name', read_only=True)
    
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'customer', 'customer_name', 'address', 'address_details', 
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_name', 'address_details']


class CustomerContactSerializer(serializers.ModelSerializer):
    """Serializer for CustomerContact model"""
    
    contact_details = ContactPersonSerializer(source='contact', read_only=True)
    customer_name = serializers.CharField(source='customer.display_name', read_only=True)
    
    class Meta:
        model = CustomerContact
        fields = [
            'id', 'customer', 'customer_name', 'contact', 'contact_details', 
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_name', 'contact_details']


class CustomerInteractionSerializer(serializers.ModelSerializer):
    """Serializer for CustomerInteraction model"""
    
    customer_name = serializers.CharField(source='customer.display_name', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    interaction_type_display = serializers.CharField(
        source='get_interaction_type_display', 
        read_only=True
    )
    
    class Meta:
        model = CustomerInteraction
        fields = [
            'id', 'customer', 'customer_name', 'interaction_type', 
            'interaction_type_display', 'subject', 'content', 'interaction_date',
            'employee', 'employee_name', 'follow_up_required', 'follow_up_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'customer_name', 
            'employee_name', 'interaction_type_display'
        ]


class CustomerDetailSerializer(CustomerSerializer):
    """Detailed Customer serializer with related data"""
    
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    contacts = CustomerContactSerializer(many=True, read_only=True)
    recent_interactions = serializers.SerializerMethodField()
    quotes_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    
    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + [
            'addresses', 'contacts', 'recent_interactions', 
            'quotes_count', 'projects_count'
        ]
    
    def get_recent_interactions(self, obj):
        """Get last 5 interactions"""
        interactions = obj.interactions.order_by('-interaction_date')[:5]
        return CustomerInteractionSerializer(interactions, many=True).data
    
    def get_quotes_count(self, obj):
        """Get total quotes count"""
        return obj.quotes.count()
    
    def get_projects_count(self, obj):
        """Get total projects count"""
        return obj.projects.count()