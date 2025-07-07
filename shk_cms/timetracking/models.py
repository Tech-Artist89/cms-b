"""
Time Tracking Models für SHK-CMS

Modelle für Zeiterfassung
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime, date, timedelta
from shk_cms.core.models import BaseModel
from shk_cms.customers.models import Customer
from shk_cms.projects.models import Project


class TimeEntry(BaseModel):
    """
    Zeiterfassung
    """
    ENTRY_TYPES = [
        ('work', 'Arbeitszeit'),
        ('break', 'Pause'),
        ('travel', 'Fahrtzeit'),
        ('overtime', 'Überstunden'),
        ('vacation', 'Urlaub'),
        ('sick', 'Krankheit'),
        ('training', 'Schulung'),
    ]
    
    # Grunddaten
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='work')
    
    # Zeitinformationen
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Projektbezug
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='time_entries')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='time_entries')
    
    # Tätigkeitsbeschreibung
    description = models.TextField()
    
    # Lokation
    location = models.CharField(max_length=200, blank=True, null=True)
    
    # Status
    is_billable = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_invoiced = models.BooleanField(default=False)
    
    # Approval
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_time_entries'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    
    # Zusätzliche Informationen
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Zeiteintrag'
        verbose_name_plural = 'Zeiteinträge'
        ordering = ['-date', '-start_time']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.duration_hours}h)"
        
    def save(self, *args, **kwargs):
        """Automatische Berechnung der Dauer"""
        if self.start_time and self.end_time and not self.duration_hours:
            # Berechnung der Dauer
            start_datetime = datetime.combine(date.today(), self.start_time)
            end_datetime = datetime.combine(date.today(), self.end_time)
            
            # Behandlung von Mitternachtsüberschreitung
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
                
            duration_delta = end_datetime - start_datetime
            self.duration_hours = Decimal(str(duration_delta.total_seconds() / 3600))
            
        super().save(*args, **kwargs)
        
    @property
    def duration_formatted(self):
        """Formatierte Dauer (HH:MM)"""
        if self.duration_hours:
            hours = int(self.duration_hours)
            minutes = int((self.duration_hours - hours) * 60)
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"


class Timesheet(BaseModel):
    """
    Stundenzettel (Zusammenfassung für einen Zeitraum)
    """
    TIMESHEET_STATUS = [
        ('draft', 'Entwurf'),
        ('submitted', 'Eingereicht'),
        ('approved', 'Genehmigt'),
        ('rejected', 'Abgelehnt'),
        ('paid', 'Bezahlt'),
    ]
    
    # Grunddaten
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timesheets')
    
    # Zeitraum
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=TIMESHEET_STATUS, default='draft')
    
    # Summen
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    billable_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    
    # Approval
    submitted_date = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_timesheets'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    
    # Notizen
    employee_notes = models.TextField(blank=True, null=True)
    manager_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Stundenzettel'
        verbose_name_plural = 'Stundenzettel'
        ordering = ['-start_date']
        unique_together = ['employee', 'start_date', 'end_date']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.start_date} bis {self.end_date}"
        
    def calculate_totals(self):
        """Berechnung der Gesamtstunden"""
        time_entries = TimeEntry.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        self.total_hours = sum(
            entry.duration_hours or Decimal('0.00') 
            for entry in time_entries.filter(entry_type='work')
        )
        
        self.billable_hours = sum(
            entry.duration_hours or Decimal('0.00') 
            for entry in time_entries.filter(entry_type='work', is_billable=True)
        )
        
        self.overtime_hours = sum(
            entry.duration_hours or Decimal('0.00') 
            for entry in time_entries.filter(entry_type='overtime')
        )
        
        self.save()
        
    @property
    def period_display(self):
        """Formatierte Zeitraum-Anzeige"""
        return f"{self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}"


class WorkSchedule(BaseModel):
    """
    Arbeitsplan/Schichtplan
    """
    SCHEDULE_TYPES = [
        ('regular', 'Reguläre Arbeitszeit'),
        ('overtime', 'Überstunden'),
        ('night_shift', 'Nachtschicht'),
        ('weekend', 'Wochenende'),
        ('holiday', 'Feiertag'),
    ]
    
    # Grunddaten
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_schedules')
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='regular')
    
    # Zeitinformationen
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.50'))  # 30 Minuten Standard
    
    # Projektbezug
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='work_schedules')
    
    # Lokation
    location = models.CharField(max_length=200, blank=True, null=True)
    
    # Notizen
    notes = models.TextField(blank=True, null=True)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Arbeitsplan'
        verbose_name_plural = 'Arbeitspläne'
        ordering = ['date', 'start_time']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.start_time}-{self.end_time})"
        
    @property
    def planned_hours(self):
        """Geplante Arbeitszeit"""
        start_datetime = datetime.combine(date.today(), self.start_time)
        end_datetime = datetime.combine(date.today(), self.end_time)
        
        # Behandlung von Mitternachtsüberschreitung
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
            
        duration_delta = end_datetime - start_datetime
        planned_hours = Decimal(str(duration_delta.total_seconds() / 3600))
        
        # Pause abziehen
        return planned_hours - self.break_duration
        
    @property
    def is_past_due(self):
        """Prüft ob der Arbeitsplan in der Vergangenheit liegt"""
        return self.date < date.today()


class OvertimeRequest(BaseModel):
    """
    Überstunden-Anfrage
    """
    REQUEST_STATUS = [
        ('pending', 'Ausstehend'),
        ('approved', 'Genehmigt'),
        ('rejected', 'Abgelehnt'),
    ]
    
    # Grunddaten
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='overtime_requests')
    
    # Überstunden-Details
    date = models.DateField()
    planned_hours = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.25'))])
    reason = models.TextField()
    
    # Projektbezug
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='overtime_requests')
    
    # Status
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    
    # Approval
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_overtime_requests'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Überstunden-Anfrage'
        verbose_name_plural = 'Überstunden-Anfragen'
        ordering = ['-requested_date']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.planned_hours}h)"