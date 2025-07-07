"""
Employee Models für SHK-CMS

Modelle für Personalverwaltung
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from shk_cms.core.models import BaseModel, Address, ContactPerson


class Employee(BaseModel):
    """
    Mitarbeiter (Erweitert das Django User Model)
    """
    EMPLOYMENT_STATUS = [
        ('active', 'Aktiv'),
        ('inactive', 'Inaktiv'),
        ('vacation', 'Urlaub'),
        ('sick', 'Krank'),
        ('terminated', 'Gekündigt'),
    ]
    
    EMPLOYMENT_TYPES = [
        ('full_time', 'Vollzeit'),
        ('part_time', 'Teilzeit'),
        ('apprentice', 'Auszubildender'),
        ('freelancer', 'Freiberufler'),
        ('temporary', 'Zeitarbeit'),
    ]
    
    # Verknüpfung mit Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    
    # Personaldaten
    employee_number = models.CharField(max_length=20, unique=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    
    # Persönliche Daten
    birth_date = models.DateField(blank=True, null=True)
    phone_private = models.CharField(max_length=50, blank=True, null=True)
    phone_business = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    
    # Arbeitsplatz-Informationen
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='subordinates'
    )
    
    # Beschäftigungsdaten
    hire_date = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    
    # Arbeitszeiten
    weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=40.00)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Qualifikationen
    qualifications = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Adresse
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Mitarbeiter'
        verbose_name_plural = 'Mitarbeiter'
        ordering = ['employee_number']
        
    def __str__(self):
        return f"{self.employee_number} - {self.user.get_full_name()}"
        
    def save(self, *args, **kwargs):
        """Automatische Generierung der Mitarbeiternummer"""
        if not self.employee_number:
            # Einfache Mitarbeiternummer-Generierung
            last_employee = Employee.objects.filter(
                employee_number__startswith='M'
            ).order_by('-employee_number').first()
            
            if last_employee:
                try:
                    last_number = int(last_employee.employee_number[1:])
                    self.employee_number = f"M{last_number + 1:04d}"
                except (ValueError, TypeError):
                    self.employee_number = "M0001"
            else:
                self.employee_number = "M0001"
                
        super().save(*args, **kwargs)
        
    @property
    def full_name(self):
        """Vollständiger Name"""
        return self.user.get_full_name()
        
    @property
    def is_active(self):
        """Prüft ob der Mitarbeiter aktiv ist"""
        return self.employment_status == 'active'


class EmployeeSkill(BaseModel):
    """
    Mitarbeiterfähigkeiten und Qualifikationen
    """
    SKILL_CATEGORIES = [
        ('technical', 'Technische Fähigkeiten'),
        ('certification', 'Zertifizierungen'),
        ('language', 'Sprachen'),
        ('software', 'Software-Kenntnisse'),
        ('safety', 'Sicherheit'),
        ('other', 'Sonstiges'),
    ]
    
    SKILL_LEVELS = [
        ('beginner', 'Anfänger'),
        ('intermediate', 'Fortgeschritten'),
        ('advanced', 'Experte'),
        ('expert', 'Spezialist'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='skills')
    
    # Fähigkeitsdetails
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES, default='technical')
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='intermediate')
    
    # Zusätzliche Informationen
    description = models.TextField(blank=True, null=True)
    acquired_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Zertifizierungsdetails
    certification_body = models.CharField(max_length=100, blank=True, null=True)
    certificate_number = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Mitarbeiterfähigkeit'
        verbose_name_plural = 'Mitarbeiterfähigkeiten'
        unique_together = ['employee', 'name', 'category']
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.name}"
        
    @property
    def is_expired(self):
        """Prüft ob die Zertifizierung abgelaufen ist"""
        from datetime import date
        return self.expiry_date and self.expiry_date < date.today()


class EmployeeDocument(BaseModel):
    """
    Mitarbeiterdokumente
    """
    DOCUMENT_TYPES = [
        ('contract', 'Arbeitsvertrag'),
        ('id_copy', 'Ausweiskopie'),
        ('certificate', 'Zertifikat'),
        ('reference', 'Zeugnis'),
        ('medical', 'Gesundheitszeugnis'),
        ('training', 'Schulungsnachweis'),
        ('other', 'Sonstiges'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='employees/documents/')
    description = models.TextField(blank=True, null=True)
    
    # Gültigkeitsdaten
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Metadaten
    file_size = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Mitarbeiterdokument'
        verbose_name_plural = 'Mitarbeiterdokumente'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Bestimmung der Dateigröße"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
        
    @property
    def is_expired(self):
        """Prüft ob das Dokument abgelaufen ist"""
        from datetime import date
        return self.expiry_date and self.expiry_date < date.today()


class EmployeeAvailability(BaseModel):
    """
    Mitarbeiterverfügbarkeit (Urlaub, Krankheit, etc.)
    """
    AVAILABILITY_TYPES = [
        ('vacation', 'Urlaub'),
        ('sick_leave', 'Krankheit'),
        ('training', 'Schulung'),
        ('business_trip', 'Dienstreise'),
        ('unavailable', 'Nicht verfügbar'),
        ('available', 'Verfügbar'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='availabilities')
    
    # Verfügbarkeitsdetails
    availability_type = models.CharField(max_length=20, choices=AVAILABILITY_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Zusätzliche Informationen
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_availabilities'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Mitarbeiterverfügbarkeit'
        verbose_name_plural = 'Mitarbeiterverfügbarkeiten'
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.get_availability_type_display()}: {self.start_date} bis {self.end_date}"
        
    @property
    def duration_days(self):
        """Dauer in Tagen"""
        return (self.end_date - self.start_date).days + 1
        
    @property
    def is_current(self):
        """Prüft ob die Verfügbarkeit aktuell ist"""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date