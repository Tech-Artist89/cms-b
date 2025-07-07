"""
Views for Customer models
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q

from .models import Customer, CustomerAddress, CustomerContact, CustomerInteraction
from .serializers import (
    CustomerSerializer, CustomerDetailSerializer,
    CustomerAddressSerializer, CustomerContactSerializer, 
    CustomerInteractionSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model"""
    
    queryset = Customer.objects.select_related('company', 'sales_representative').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_type', 'category', 'is_active', 'is_blocked', 'sales_representative']
    search_fields = ['customer_number', 'first_name', 'last_name', 'email', 'phone', 'company__name']
    ordering_fields = ['customer_number', 'created_at', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by sales representative if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(sales_representative=self.request.user) | 
                Q(sales_representative__isnull=True)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get customer statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_count': queryset.count(),
            'active_count': queryset.filter(is_active=True).count(),
            'blocked_count': queryset.filter(is_blocked=True).count(),
            'private_count': queryset.filter(customer_type='private').count(),
            'business_count': queryset.filter(customer_type='business').count(),
            'category_breakdown': {
                'A': queryset.filter(category='A').count(),
                'B': queryset.filter(category='B').count(),
                'C': queryset.filter(category='C').count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def add_interaction(self, request, pk=None):
        """Add interaction to customer"""
        customer = self.get_object()
        serializer = CustomerInteractionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(customer=customer, employee=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Get customer interactions"""
        customer = self.get_object()
        interactions = customer.interactions.order_by('-interaction_date')
        serializer = CustomerInteractionSerializer(interactions, many=True)
        return Response(serializer.data)


class CustomerAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomerAddress model"""
    
    queryset = CustomerAddress.objects.select_related('customer', 'address').all()
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'is_primary', 'address__type']
    ordering = ['-created_at']


class CustomerContactViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomerContact model"""
    
    queryset = CustomerContact.objects.select_related('customer', 'contact').all()
    serializer_class = CustomerContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'is_primary']
    ordering = ['-created_at']


class CustomerInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomerInteraction model"""
    
    queryset = CustomerInteraction.objects.select_related('customer', 'employee').all()
    serializer_class = CustomerInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'interaction_type', 'employee', 'follow_up_required']
    search_fields = ['subject', 'content']
    ordering_fields = ['interaction_date', 'created_at']
    ordering = ['-interaction_date']
    
    def get_queryset(self):
        """Filter interactions based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user's customers if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__sales_representative=self.request.user) |
                Q(employee=self.request.user)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def follow_ups(self, request):
        """Get interactions requiring follow-up"""
        queryset = self.get_queryset().filter(
            follow_up_required=True,
            follow_up_date__isnull=False
        ).order_by('follow_up_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)