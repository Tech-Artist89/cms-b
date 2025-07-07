"""
Invoice Models für SHK-CMS

Modelle für Rechnungsstellung und Mahnwesen
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date, timedelta
from shk_cms.core.models import BaseModel
from shk_cms.customers.models import Customer
from shk_cms.projects.models import Project


class Invoice(BaseModel):
    """
    Rechnung
    """
    INVOICE_STATUS = [
        ('draft', 'Entwurf'),
        ('sent', 'Versendet'),
        ('paid', 'Bezahlt'),
        ('overdue', 'Überfällig'),
        ('cancelled', 'Storniert'),
        ('refunded', 'Erstattet'),
    ]
    
    INVOICE_TYPES = [
        ('invoice', 'Rechnung'),
        ('credit_note', 'Gutschrift'),
        ('reminder', 'Mahnung'),
        ('final_reminder', 'Letzte Mahnung'),
    ]
    
    # Grunddaten
    invoice_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='invoices')
    
    # Rechnungsdetails
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPES, default='invoice')
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    
    # Datumsinformationen
    invoice_date = models.DateField(default=date.today)
    due_date = models.DateField()
    payment_date = models.DateField(blank=True, null=True)
    
    # Beträge
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('19.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Textfelder
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    payment_terms = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    # Zahlungsreferenz
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Zuweisungen
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices_created')
    
    class Meta:
        verbose_name = 'Rechnung'
        verbose_name_plural = 'Rechnungen'
        ordering = ['-invoice_date', '-invoice_number']
        
    def __str__(self):
        return f"Rechnung {self.invoice_number} - {self.customer}"
        
    def save(self, *args, **kwargs):
        """Automatische Generierung der Rechnungsnummer und Fälligkeitsdatum"""
        if not self.invoice_number:
            # Einfache Rechnungsnummer-Generierung
            today = date.today()
            year = today.year
            
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f'R{year}'
            ).order_by('-invoice_number').first()
            
            if last_invoice:
                try:
                    last_number = int(last_invoice.invoice_number[5:])
                    self.invoice_number = f"R{year}{last_number + 1:04d}"
                except (ValueError, TypeError):
                    self.invoice_number = f"R{year}0001"
            else:
                self.invoice_number = f"R{year}0001"
                
        # Fälligkeitsdatum setzen falls nicht vorhanden
        if not self.due_date:
            payment_terms_days = 14
            if self.customer and self.customer.payment_terms_days:
                payment_terms_days = self.customer.payment_terms_days
            self.due_date = self.invoice_date + timedelta(days=payment_terms_days)
            
        super().save(*args, **kwargs)
        
    def calculate_totals(self):
        """Berechnung der Gesamtsummen"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.discount_amount = self.subtotal * (self.discount_percent / 100)
        discounted_subtotal = self.subtotal - self.discount_amount
        self.tax_amount = discounted_subtotal * (self.tax_rate / 100)
        self.total_amount = discounted_subtotal + self.tax_amount
        self.save()
        
    @property
    def outstanding_amount(self):
        """Offener Betrag"""
        return self.total_amount - self.paid_amount
        
    @property
    def is_overdue(self):
        """Prüft ob die Rechnung überfällig ist"""
        return self.due_date < date.today() and self.status not in ['paid', 'cancelled', 'refunded']
        
    @property
    def days_overdue(self):
        """Anzahl Tage überfällig"""
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0


class InvoiceItem(BaseModel):
    """
    Rechnungspositionen
    """
    ITEM_TYPES = [
        ('material', 'Material'),
        ('service', 'Dienstleistung'),
        ('labor', 'Arbeitszeit'),
        ('discount', 'Rabatt'),
        ('text', 'Textposition'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
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
        verbose_name = 'Rechnungsposition'
        verbose_name_plural = 'Rechnungspositionen'
        ordering = ['position_number']
        unique_together = ['invoice', 'position_number']
        
    def __str__(self):
        return f"{self.invoice.invoice_number} - Pos. {self.position_number}: {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Berechnung des Gesamtpreises"""
        if self.item_type != 'text':
            # Rabatt anwenden
            discounted_price = self.unit_price * (1 - self.discount_percent / 100)
            self.total_price = self.quantity * discounted_price
        else:
            self.total_price = Decimal('0.00')
            
        super().save(*args, **kwargs)
        
        # Rechnung-Summen neu berechnen
        self.invoice.calculate_totals()


class Payment(BaseModel):
    """
    Zahlungseingänge
    """
    PAYMENT_METHODS = [
        ('bank_transfer', 'Überweisung'),
        ('cash', 'Bargeld'),
        ('card', 'Kartenzahlung'),
        ('check', 'Scheck'),
        ('direct_debit', 'Lastschrift'),
        ('other', 'Sonstiges'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    
    # Zahlungsdetails
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField(default=date.today)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    
    # Referenzen
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    bank_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    
    # Zuweisungen
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Zahlung'
        verbose_name_plural = 'Zahlungen'
        ordering = ['-payment_date']
        
    def __str__(self):
        return f"Zahlung {self.amount}€ für {self.invoice.invoice_number}"
        
    def save(self, *args, **kwargs):
        """Aktualisierung des Zahlungsstatus der Rechnung"""
        super().save(*args, **kwargs)
        
        # Bezahlten Betrag der Rechnung aktualisieren
        total_paid = sum(payment.amount for payment in self.invoice.payments.all())
        self.invoice.paid_amount = total_paid
        
        # Status der Rechnung aktualisieren
        if total_paid >= self.invoice.total_amount:
            self.invoice.status = 'paid'
            self.invoice.payment_date = self.payment_date
        elif total_paid > 0:
            self.invoice.status = 'sent'  # Teilzahlung
            
        self.invoice.save()


class Reminder(BaseModel):
    """
    Mahnungen
    """
    REMINDER_LEVELS = [
        (1, '1. Mahnung'),
        (2, '2. Mahnung'),
        (3, '3. Mahnung (Letzte Mahnung)'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminders')
    
    # Mahndetails
    reminder_level = models.IntegerField(choices=REMINDER_LEVELS)
    reminder_date = models.DateField(default=date.today)
    reminder_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateField(blank=True, null=True)
    
    # Textfelder
    reminder_text = models.TextField(blank=True, null=True)
    
    # Zuweisungen
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Mahnung'
        verbose_name_plural = 'Mahnungen'
        ordering = ['-reminder_date', '-reminder_level']
        unique_together = ['invoice', 'reminder_level']
        
    def __str__(self):
        return f"{self.get_reminder_level_display()} für {self.invoice.invoice_number}"