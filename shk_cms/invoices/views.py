"""
Views for Invoice models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum
from decimal import Decimal

from .models import Invoice, InvoiceItem, Payment, Reminder
from .serializers import (
    InvoiceSerializer, InvoiceDetailSerializer, InvoiceCreateUpdateSerializer,
    InvoiceItemSerializer, PaymentSerializer, ReminderSerializer, InvoiceStatsSerializer
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model"""
    
    queryset = Invoice.objects.select_related('customer', 'project', 'created_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['invoice_type', 'status', 'customer', 'project', 'created_by']
    search_fields = ['invoice_number', 'title', 'customer__customer_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InvoiceCreateUpdateSerializer
        return InvoiceSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get invoice statistics"""
        queryset = self.get_queryset()
        stats_data = {
            'total_count': queryset.count(),
            'draft_count': queryset.filter(status='draft').count(),
            'sent_count': queryset.filter(status='sent').count(),
            'paid_count': queryset.filter(status='paid').count(),
            'overdue_count': queryset.filter(status='overdue').count(),
            'total_amount': queryset.aggregate(sum=Sum('total_amount'))['sum'] or Decimal('0'),
            'outstanding_amount': sum(inv.outstanding_amount for inv in queryset),
            'paid_amount': queryset.aggregate(sum=Sum('paid_amount'))['sum'] or Decimal('0'),
        }
        return Response(stats_data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices"""
        from datetime import date
        queryset = self.get_queryset().filter(
            due_date__lt=date.today(),
            status__in=['sent', 'overdue']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for InvoiceItem model"""
    
    queryset = InvoiceItem.objects.select_related('invoice').all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['invoice', 'item_type']
    ordering = ['position_number']


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model"""
    
    queryset = Payment.objects.select_related('invoice', 'recorded_by').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['invoice', 'payment_method', 'recorded_by']
    search_fields = ['reference_number', 'bank_reference']
    ordering = ['-payment_date']


class ReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for Reminder model"""
    
    queryset = Reminder.objects.select_related('invoice', 'created_by').all()
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['invoice', 'reminder_level', 'is_sent']
    ordering = ['-reminder_date']