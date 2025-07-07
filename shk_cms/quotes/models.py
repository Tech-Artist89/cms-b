"""
Quote Models für SHK-CMS

Modelle für Angebotswesen
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from shk_cms.core.models import BaseModel
from shk_cms.customers.models import Customer


class Quote(BaseModel):
    """
    Angebot
    """
    QUOTE_STATUS = [
        ('draft', 'Entwurf'),
        ('sent', 'Versendet'),
        ('accepted', 'Angenommen'),
        ('rejected', 'Abgelehnt'),
        ('expired', 'Abgelaufen'),
        ('cancelled', 'Storniert'),
    ]
    
    # Grunddaten
    quote_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    
    # Status und Versionierung
    status = models.CharField(max_length=20, choices=QUOTE_STATUS, default='draft')
    version = models.IntegerField(default=1)
    
    # Datumsinformationen
    quote_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    
    # Beträge
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('19.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Textfelder
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    # Zuweisungen
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes_created')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='quotes_assigned'
    )
    
    class Meta:
        verbose_name = 'Angebot'
        verbose_name_plural = 'Angebote'
        ordering = ['-quote_date', '-quote_number']
        
    def __str__(self):
        return f"Angebot {self.quote_number} - {self.customer}"
        
    def save(self, *args, **kwargs):
        """Automatische Generierung der Angebotsnummer"""
        if not self.quote_number:
            # Einfache Angebotsnummer-Generierung
            from datetime import date
            today = date.today()
            year = today.year
            
            last_quote = Quote.objects.filter(
                quote_number__startswith=f'A{year}'
            ).order_by('-quote_number').first()
            
            if last_quote:
                try:
                    last_number = int(last_quote.quote_number[5:])
                    self.quote_number = f"A{year}{last_number + 1:04d}"
                except (ValueError, TypeError):
                    self.quote_number = f"A{year}0001"
            else:
                self.quote_number = f"A{year}0001"
                
        super().save(*args, **kwargs)
        
    def calculate_totals(self):
        """Berechnung der Gesamtsummen"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.discount_amount = self.subtotal * (self.discount_percent / 100)
        discounted_subtotal = self.subtotal - self.discount_amount
        self.tax_amount = discounted_subtotal * (self.tax_rate / 100)
        self.total_amount = discounted_subtotal + self.tax_amount
        self.save()


class QuoteItem(BaseModel):
    """
    Angebotspositionen
    """
    ITEM_TYPES = [
        ('material', 'Material'),
        ('service', 'Dienstleistung'),
        ('labor', 'Arbeitszeit'),
        ('discount', 'Rabatt'),
        ('text', 'Textposition'),
    ]
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    position_number = models.IntegerField()
    
    # Positionsdetails
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='material')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Mengen und Preise
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    unit = models.CharField(max_length=20, default='Stück')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Artikel-/Servicenummer
    item_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Rabatt auf Position
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        verbose_name = 'Angebotsposition'
        verbose_name_plural = 'Angebotspositionen'
        ordering = ['position_number']
        unique_together = ['quote', 'position_number']
        
    def __str__(self):
        return f"{self.quote.quote_number} - Pos. {self.position_number}: {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Berechnung des Gesamtpreises"""
        if self.item_type != 'text':
            # Rabatt anwenden
            discounted_price = self.unit_price * (1 - self.discount_percent / 100)
            self.total_price = self.quantity * discounted_price
        else:
            self.total_price = Decimal('0.00')
            
        super().save(*args, **kwargs)
        
        # Angebot-Summen neu berechnen
        self.quote.calculate_totals()


class QuoteDocument(BaseModel):
    """
    Angebotsdokumente (PDFs, Bilder etc.)
    """
    DOCUMENT_TYPES = [
        ('quote_pdf', 'Angebot PDF'),
        ('attachment', 'Anhang'),
        ('technical_drawing', 'Technische Zeichnung'),
        ('photo', 'Foto'),
        ('calculation', 'Kalkulation'),
    ]
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='quotes/documents/')
    description = models.TextField(blank=True, null=True)
    
    # Metadaten
    file_size = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Angebotsdokument'
        verbose_name_plural = 'Angebotsdokumente'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.quote.quote_number} - {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Bestimmung der Dateigröße"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)