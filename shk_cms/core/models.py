"""
Core Models für SHK-CMS

Diese Modelle enthalten gemeinsame Funktionalität und Basis-Modelle
für alle anderen Apps.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class TimeStampedModel(models.Model):
    """
    Abstrakte Basisklasse für alle Modelle mit Zeitstempel
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstrakte Basisklasse für Modelle mit UUID als Primary Key
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """
    Kombinierte Basisklasse mit UUID und Zeitstempel
    """
    class Meta:
        abstract = True


class Address(BaseModel):
    """
    Adressmodell für Kunden, Lieferadressen etc.
    """
    ADDRESS_TYPES = [
        ('billing', 'Rechnungsadresse'),
        ('shipping', 'Lieferadresse'),
        ('work', 'Arbeitsadresse'),
        ('home', 'Privatadresse'),
    ]
    
    type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='billing')
    street = models.CharField(max_length=255)
    street_number = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Deutschland')
    
    # Zusätzliche Felder
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Adresse'
        verbose_name_plural = 'Adressen'
        
    def __str__(self):
        return f"{self.street} {self.street_number}, {self.postal_code} {self.city}"
        
    @property
    def full_address(self):
        """Vollständige Adresse als String"""
        parts = [f"{self.street} {self.street_number}"]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.append(f"{self.postal_code} {self.city}")
        if self.country != 'Deutschland':
            parts.append(self.country)
        return ", ".join(parts)


class ContactPerson(BaseModel):
    """
    Ansprechpartner für Kunden
    """
    SALUTATION_CHOICES = [
        ('herr', 'Herr'),
        ('frau', 'Frau'),
        ('firma', 'Firma'),
    ]
    
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    
    # Kontaktdaten
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Ansprechpartner'
        verbose_name_plural = 'Ansprechpartner'
        
    def __str__(self):
        name_parts = []
        if self.salutation:
            name_parts.append(self.get_salutation_display())
        if self.title:
            name_parts.append(self.title)
        name_parts.extend([self.first_name, self.last_name])
        return " ".join(name_parts)
        
    @property
    def full_name(self):
        """Vollständiger Name ohne Anrede"""
        return f"{self.first_name} {self.last_name}"


class Company(BaseModel):
    """
    Firmeninformationen (für eigene Firma und Kunden)
    """
    name = models.CharField(max_length=200)
    legal_form = models.CharField(max_length=50, blank=True, null=True)  # GmbH, AG, etc.
    trade_register_number = models.CharField(max_length=50, blank=True, null=True)
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Kontaktdaten
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Bankdaten
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    bic = models.CharField(max_length=11, blank=True, null=True)
    
    # Logo und Branding
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    is_own_company = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmen'
        
    def __str__(self):
        return self.name


class Note(BaseModel):
    """
    Notizen zu Kunden, Projekten etc.
    """
    NOTE_TYPES = [
        ('general', 'Allgemein'),
        ('phone', 'Telefonat'),
        ('email', 'E-Mail'),
        ('meeting', 'Termin'),
        ('internal', 'Intern'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    
    # Verknüpfung mit anderen Objekten über Generic Foreign Key
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Benutzer der die Notiz erstellt hat
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Notiz'
        verbose_name_plural = 'Notizen'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title