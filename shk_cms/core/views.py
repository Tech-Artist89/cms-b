"""
Views for Core models
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Address, ContactPerson, Company, Note
from .serializers import (
    AddressSerializer, ContactPersonSerializer, 
    CompanySerializer, NoteSerializer
)


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for Address model"""
    
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'country', 'city']
    search_fields = ['street', 'city', 'postal_code']
    ordering_fields = ['city', 'created_at']
    ordering = ['-created_at']


class ContactPersonViewSet(viewsets.ModelViewSet):
    """ViewSet for ContactPerson model"""
    
    queryset = ContactPerson.objects.all()
    serializer_class = ContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['salutation', 'is_primary']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['last_name', 'created_at']
    ordering = ['last_name', 'first_name']


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model"""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['legal_form', 'is_own_company']
    search_fields = ['name', 'email', 'tax_number', 'vat_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Note model"""
    
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['note_type', 'author', 'content_type']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notes by content object if specified"""
        queryset = super().get_queryset()
        
        # Filter by content_type and object_id if provided
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        if content_type and object_id:
            queryset = queryset.filter(
                content_type__model=content_type,
                object_id=object_id
            )
            
        return queryset