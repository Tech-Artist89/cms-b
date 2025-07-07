"""
Serializers for Invoice models
"""

from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, Reminder
from shk_cms.customers.serializers import CustomerSerializer
from shk_cms.projects.serializers import ProjectSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model"""
    
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'position_number', 'item_type', 'item_type_display', 
            'title', 'description', 'quantity', 'unit', 'unit_price', 
            'total_price', 'item_number', 'discount_percent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at', 'item_type_display']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'payment_date', 'payment_method', 'payment_method_display',
            'reference_number', 'bank_reference', 'notes', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'recorded_by', 'recorded_by_name', 'payment_method_display',
            'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set recorded_by to current user"""
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model"""
    
    reminder_level_display = serializers.CharField(source='get_reminder_level_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'reminder_level', 'reminder_level_display', 'reminder_date', 
            'reminder_fee', 'is_sent', 'sent_date', 'reminder_text',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_by_name', 'reminder_level_display',
            'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    
    customer_details = CustomerSerializer(source='customer', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    outstanding_amount = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_details', 'project', 'project_details',
            'invoice_type', 'invoice_type_display', 'status', 'status_display',
            'invoice_date', 'due_date', 'payment_date', 'subtotal', 'tax_rate',
            'tax_amount', 'total_amount', 'discount_percent', 'discount_amount',
            'paid_amount', 'outstanding_amount', 'is_overdue', 'days_overdue',
            'title', 'description', 'payment_terms', 'internal_notes',
            'payment_reference', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
            'discount_amount', 'paid_amount', 'outstanding_amount', 'is_overdue',
            'days_overdue', 'created_at', 'updated_at', 'customer_details',
            'project_details', 'invoice_type_display', 'status_display', 'created_by_name'
        ]
        
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class InvoiceDetailSerializer(InvoiceSerializer):
    """Detailed Invoice serializer with items, payments and reminders"""
    
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    reminders = ReminderSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    payments_count = serializers.SerializerMethodField()
    
    class Meta(InvoiceSerializer.Meta):
        fields = InvoiceSerializer.Meta.fields + [
            'items', 'payments', 'reminders', 'items_count', 'payments_count'
        ]
    
    def get_items_count(self, obj):
        """Get total items count"""
        return obj.items.count()
    
    def get_payments_count(self, obj):
        """Get total payments count"""
        return obj.payments.count()


class InvoiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating invoices with items"""
    
    items = InvoiceItemSerializer(many=True, required=False)
    
    class Meta:
        model = Invoice
        fields = [
            'customer', 'project', 'invoice_type', 'status', 'due_date',
            'tax_rate', 'discount_percent', 'title', 'description',
            'payment_terms', 'internal_notes', 'payment_reference', 'items'
        ]
        
    def create(self, validated_data):
        """Create invoice with items"""
        items_data = validated_data.pop('items', [])
        validated_data['created_by'] = self.context['request'].user
        
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
            
        invoice.calculate_totals()
        return invoice
        
    def update(self, instance, validated_data):
        """Update invoice and items"""
        items_data = validated_data.pop('items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
                
            instance.calculate_totals()
            
        return instance


class InvoiceStatsSerializer(serializers.Serializer):
    """Serializer for invoice statistics"""
    
    total_count = serializers.IntegerField()
    draft_count = serializers.IntegerField()
    sent_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)