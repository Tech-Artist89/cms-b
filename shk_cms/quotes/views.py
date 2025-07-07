"""
Views for Quote models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import Quote, QuoteItem, QuoteDocument
from .serializers import (
    QuoteSerializer, QuoteDetailSerializer, QuoteCreateUpdateSerializer,
    QuoteItemSerializer, QuoteDocumentSerializer
)


class QuoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Quote model"""
    
    queryset = Quote.objects.select_related('customer', 'created_by', 'assigned_to').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'customer', 'created_by', 'assigned_to']
    search_fields = ['quote_number', 'title', 'customer__customer_number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['quote_date', 'valid_until', 'total_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return QuoteDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return QuoteCreateUpdateSerializer
        return QuoteSerializer
    
    def get_queryset(self):
        """Filter quotes based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's quotes if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(assigned_to=self.request.user) |
                Q(customer__sales_representative=self.request.user)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get quote statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_count': queryset.count(),
            'draft_count': queryset.filter(status='draft').count(),
            'sent_count': queryset.filter(status='sent').count(),
            'accepted_count': queryset.filter(status='accepted').count(),
            'rejected_count': queryset.filter(status='rejected').count(),
            'expired_count': queryset.filter(status='expired').count(),
            'total_value': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'avg_value': queryset.aggregate(avg=Sum('total_amount'))['avg'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get quotes expiring within next 7 days"""
        from datetime import date, timedelta
        
        expiring_date = date.today() + timedelta(days=7)
        queryset = self.get_queryset().filter(
            valid_until__lte=expiring_date,
            valid_until__gte=date.today(),
            status__in=['draft', 'sent']
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a duplicate of the quote"""
        original_quote = self.get_object()
        
        # Create new quote
        new_quote = Quote.objects.create(
            customer=original_quote.customer,
            title=f"{original_quote.title} (Kopie)",
            description=original_quote.description,
            terms_and_conditions=original_quote.terms_and_conditions,
            tax_rate=original_quote.tax_rate,
            discount_percent=original_quote.discount_percent,
            created_by=request.user
        )
        
        # Copy items
        for item in original_quote.items.all():
            QuoteItem.objects.create(
                quote=new_quote,
                position_number=item.position_number,
                item_type=item.item_type,
                title=item.title,
                description=item.description,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                item_number=item.item_number,
                discount_percent=item.discount_percent
            )
        
        new_quote.calculate_totals()
        serializer = QuoteDetailSerializer(new_quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Mark quote as sent"""
        quote = self.get_object()
        quote.status = 'sent'
        quote.save()
        
        serializer = self.get_serializer(quote)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Mark quote as accepted"""
        quote = self.get_object()
        quote.status = 'accepted'
        quote.save()
        
        serializer = self.get_serializer(quote)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Mark quote as rejected"""
        quote = self.get_object()
        quote.status = 'rejected'
        quote.save()
        
        serializer = self.get_serializer(quote)
        return Response(serializer.data)


class QuoteItemViewSet(viewsets.ModelViewSet):
    """ViewSet for QuoteItem model"""
    
    queryset = QuoteItem.objects.select_related('quote').all()
    serializer_class = QuoteItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['quote', 'item_type']
    search_fields = ['title', 'description', 'item_number']
    ordering_fields = ['position_number', 'created_at']
    ordering = ['position_number']
    
    def get_queryset(self):
        """Filter items based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's quotes if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(quote__created_by=self.request.user) |
                Q(quote__assigned_to=self.request.user) |
                Q(quote__customer__sales_representative=self.request.user)
            )
            
        return queryset


class QuoteDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for QuoteDocument model"""
    
    queryset = QuoteDocument.objects.select_related('quote', 'uploaded_by').all()
    serializer_class = QuoteDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['quote', 'document_type', 'uploaded_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter documents based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's quotes if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(quote__created_by=self.request.user) |
                Q(quote__assigned_to=self.request.user) |
                Q(quote__customer__sales_representative=self.request.user)
            )
            
        return queryset