"""
Serializers for Employee models
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, EmployeeSkill, EmployeeDocument, EmployeeAvailability
from shk_cms.core.serializers import AddressSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'is_active', 'is_staff', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'full_name']


class EmployeeSkillSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeSkill model"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeSkill
        fields = [
            'id', 'name', 'category', 'category_display', 'level', 'level_display',
            'description', 'acquired_date', 'expiry_date', 'is_expired',
            'certification_body', 'certificate_number', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'category_display', 'level_display', 'is_expired',
            'created_at', 'updated_at'
        ]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeDocument model"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'title', 
            'file', 'description', 'issue_date', 'expiry_date', 'is_expired',
            'file_size', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'uploaded_by', 'uploaded_by_name', 
            'document_type_display', 'is_expired', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        """Set uploaded_by to current user"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for EmployeeAvailability model"""
    
    availability_type_display = serializers.CharField(source='get_availability_type_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeAvailability
        fields = [
            'id', 'availability_type', 'availability_type_display', 'start_date', 
            'end_date', 'duration_days', 'reason', 'notes', 'is_approved',
            'approved_by', 'approved_by_name', 'approved_date', 'is_current',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'availability_type_display', 'duration_days', 'is_current',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at'
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    
    user_details = UserSerializer(source='user', read_only=True)
    address_details = AddressSerializer(source='address', read_only=True)
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.user.get_full_name', read_only=True)
    full_name = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'user', 'user_details', 'employment_status',
            'employment_status_display', 'employment_type', 'employment_type_display',
            'birth_date', 'phone_private', 'phone_business', 'mobile',
            'department', 'position', 'supervisor', 'supervisor_name',
            'hire_date', 'termination_date', 'weekly_hours', 'hourly_rate',
            'qualifications', 'certifications', 'notes', 'emergency_contact_name',
            'emergency_contact_phone', 'address', 'address_details',
            'full_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'employee_number', 'user_details', 'address_details',
            'employment_status_display', 'employment_type_display', 'supervisor_name',
            'full_name', 'is_active', 'created_at', 'updated_at'
        ]


class EmployeeDetailSerializer(EmployeeSerializer):
    """Detailed Employee serializer with related data"""
    
    skills = EmployeeSkillSerializer(many=True, read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    availabilities = EmployeeAvailabilitySerializer(many=True, read_only=True)
    subordinates = serializers.SerializerMethodField()
    
    # Statistics
    skills_count = serializers.SerializerMethodField()
    expired_documents_count = serializers.SerializerMethodField()
    current_availability = serializers.SerializerMethodField()
    
    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + [
            'skills', 'documents', 'availabilities', 'subordinates',
            'skills_count', 'expired_documents_count', 'current_availability'
        ]
    
    def get_subordinates(self, obj):
        """Get subordinate employees"""
        subordinates = obj.subordinates.all()
        return EmployeeSerializer(subordinates, many=True).data
    
    def get_skills_count(self, obj):
        """Get total skills count"""
        return obj.skills.count()
    
    def get_expired_documents_count(self, obj):
        """Get expired documents count"""
        from datetime import date
        return obj.documents.filter(expiry_date__lt=date.today()).count()
    
    def get_current_availability(self, obj):
        """Get current availability if any"""
        current = obj.availabilities.filter(
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).first()
        if current:
            return EmployeeAvailabilitySerializer(current).data
        return None


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating employees"""
    
    # User fields
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    password = serializers.CharField(source='user.password', write_only=True, required=False)
    
    class Meta:
        model = Employee
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'employment_status', 'employment_type', 'birth_date',
            'phone_private', 'phone_business', 'mobile', 'department',
            'position', 'supervisor', 'hire_date', 'termination_date',
            'weekly_hours', 'hourly_rate', 'qualifications', 'certifications',
            'notes', 'emergency_contact_name', 'emergency_contact_phone', 'address'
        ]
        
    def create(self, validated_data):
        """Create employee with user"""
        user_data = validated_data.pop('user', {})
        password = user_data.pop('password', None)
        
        # Create user
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
        
        # Create employee
        employee = Employee.objects.create(user=user, **validated_data)
        return employee
        
    def update(self, instance, validated_data):
        """Update employee and user"""
        user_data = validated_data.pop('user', {})
        password = user_data.pop('password', None)
        
        # Update user
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        if password:
            user.set_password(password)
        user.save()
        
        # Update employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class EmployeeStatsSerializer(serializers.Serializer):
    """Serializer for employee statistics"""
    
    total_count = serializers.IntegerField()
    active_count = serializers.IntegerField()
    inactive_count = serializers.IntegerField()
    on_vacation_count = serializers.IntegerField()
    sick_count = serializers.IntegerField()
    departments = serializers.DictField()
    avg_weekly_hours = serializers.DecimalField(max_digits=5, decimal_places=2)