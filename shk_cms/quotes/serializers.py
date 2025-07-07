"""
Serializers for Quote models
"""

from rest_framework import serializers
from .models import Quote, QuoteItem, QuoteDocument
from shk_cms.customers.serializers import CustomerSerializer


class QuoteItemSerializer(serializers.ModelSerializer):
    """Serializer for QuoteItem model"""
    
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = QuoteItem
        fields = [
            'id', 'position_number', 'item_type', 'item_type_display', 
            'title', 'description', 'quantity', 'unit', 'unit_price', 
            'total_price', 'item_number', 'discount_percent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at', 'item_type_display']


class QuoteDocumentSerializer(serializers.ModelSerializer):
    """Serializer for QuoteDocument model"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = QuoteDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'title', 
            'file', 'description', 'file_size', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'uploaded_by', 'uploaded_by_name', 
            'created_at', 'updated_at', 'document_type_display'
        ]
        
    def create(self, validated_data):
        """Set uploaded_by to current user"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class QuoteSerializer(serializers.ModelSerializer):
    """Serializer for Quote model"""
    
    customer_details = CustomerSerializer(source='customer', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'customer', 'customer_details', 'status', 'status_display',
            'version', 'quote_date', 'valid_until', 'subtotal', 'tax_rate', 
            'tax_amount', 'total_amount', 'discount_percent', 'discount_amount',
            'title', 'description', 'terms_and_conditions', 'internal_notes',
            'created_by', 'created_by_name', 'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'quote_number', 'subtotal', 'tax_amount', 'total_amount', 
            'discount_amount', 'created_at', 'updated_at', 'customer_details',
            'status_display', 'created_by_name', 'assigned_to_name'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class QuoteDetailSerializer(QuoteSerializer):
    """Detailed Quote serializer with items and documents"""
    
    items = QuoteItemSerializer(many=True, read_only=True)
    documents = QuoteDocumentSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta(QuoteSerializer.Meta):
        fields = QuoteSerializer.Meta.fields + ['items', 'documents', 'items_count']
    
    def get_items_count(self, obj):
        """Get total items count"""
        return obj.items.count()


class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating quotes with items"""
    
    items = QuoteItemSerializer(many=True, required=False)
    
    class Meta:
        model = Quote
        fields = [
            'customer', 'status', 'version', 'valid_until', 'tax_rate',
            'discount_percent', 'title', 'description', 'terms_and_conditions',
            'internal_notes', 'assigned_to', 'items'
        ]
        
    def create(self, validated_data):
        """Create quote with items"""
        items_data = validated_data.pop('items', [])
        validated_data['created_by'] = self.context['request'].user
        
        quote = Quote.objects.create(**validated_data)
        
        for item_data in items_data:
            QuoteItem.objects.create(quote=quote, **item_data)
            
        quote.calculate_totals()
        return quote
        
    def update(self, instance, validated_data):
        """Update quote and items"""
        items_data = validated_data.pop('items', None)
        
        # Update quote fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                QuoteItem.objects.create(quote=instance, **item_data)
                
            instance.calculate_totals()
            
        return instance