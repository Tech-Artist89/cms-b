"""
Customer Models für SHK-CMS

Modelle für Kundenverwaltung (CRM)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from shk_cms.core.models import BaseModel, Address, ContactPerson, Company


class Customer(BaseModel):
    """
    Hauptmodell für Kunden
    """
    CUSTOMER_TYPES = [
        ('private', 'Privatkunde'),
        ('business', 'Geschäftskunde'),
    ]
    
    CUSTOMER_CATEGORIES = [
        ('A', 'A-Kunde (Sehr wichtig)'),
        ('B', 'B-Kunde (Wichtig)'),
        ('C', 'C-Kunde (Normal)'),
    ]
    
    # Grunddaten
    customer_number = models.CharField(max_length=20, unique=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='private')
    category = models.CharField(max_length=1, choices=CUSTOMER_CATEGORIES, default='C')
    
    # Für Privatkunden
    salutation = models.CharField(max_length=10, choices=[
        ('herr', 'Herr'),
        ('frau', 'Frau'),
    ], blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    
    # Für Geschäftskunden
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Kontaktdaten
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    
    # Steuerliche Informationen
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Zahlungskonditionen
    payment_terms_days = models.IntegerField(default=14)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Status und Flags
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    
    # Zuweisungen
    sales_representative = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='customers'
    )
    
    class Meta:
        verbose_name = 'Kunde'
        verbose_name_plural = 'Kunden'
        ordering = ['customer_number']
        
    def __str__(self):
        if self.customer_type == 'private':
            name_parts = []
            if self.salutation:
                name_parts.append(self.get_salutation_display())
            if self.title:
                name_parts.append(self.title)
            name_parts.extend([self.first_name, self.last_name])
            return " ".join(filter(None, name_parts))
        else:
            return self.company.name if self.company else f"Kunde {self.customer_number}"
            
    @property
    def display_name(self):
        """Anzeigename für den Kunden"""
        return str(self)
        
    @property
    def full_name(self):
        """Vollständiger Name ohne Anrede"""
        if self.customer_type == 'private':
            return f"{self.first_name} {self.last_name}"
        else:
            return self.company.name if self.company else f"Kunde {self.customer_number}"
            
    def save(self, *args, **kwargs):
        """Automatische Generierung der Kundennummer"""
        if not self.customer_number:
            # Einfache Kundennummer-Generierung
            last_customer = Customer.objects.filter(
                customer_number__startswith='K'
            ).order_by('-customer_number').first()
            
            if last_customer:
                try:
                    last_number = int(last_customer.customer_number[1:])
                    self.customer_number = f"K{last_number + 1:06d}"
                except (ValueError, TypeError):
                    self.customer_number = "K000001"
            else:
                self.customer_number = "K000001"
                
        super().save(*args, **kwargs)


class CustomerAddress(BaseModel):
    """
    Verknüpfung zwischen Kunden und Adressen
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Kundenadresse'
        verbose_name_plural = 'Kundenadressen'
        unique_together = ['customer', 'address']
        
    def __str__(self):
        return f"{self.customer} - {self.address}"


class CustomerContact(BaseModel):
    """
    Verknüpfung zwischen Kunden und Ansprechpartnern
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    contact = models.ForeignKey(ContactPerson, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Kundenansprechpartner'
        verbose_name_plural = 'Kundenansprechpartner'
        unique_together = ['customer', 'contact']
        
    def __str__(self):
        return f"{self.customer} - {self.contact}"


class CustomerInteraction(BaseModel):
    """
    Kundeninteraktionen (Anrufe, E-Mails, Termine)
    """
    INTERACTION_TYPES = [
        ('phone_in', 'Eingehender Anruf'),
        ('phone_out', 'Ausgehender Anruf'),
        ('email_in', 'Eingehende E-Mail'),
        ('email_out', 'Ausgehende E-Mail'),
        ('meeting', 'Termin'),
        ('visit', 'Besuch'),
        ('other', 'Sonstiges'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    interaction_date = models.DateTimeField()
    
    # Verknüpfung mit Mitarbeiter
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Zusätzliche Informationen
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Kundeninteraktion'
        verbose_name_plural = 'Kundeninteraktionen'
        ordering = ['-interaction_date']
        
    def __str__(self):
        return f"{self.customer} - {self.get_interaction_type_display()}: {self.subject}"