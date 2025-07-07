"""
Schedule Models für SHK-CMS

Modelle für Terminplanung
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, date
from shk_cms.core.models import BaseModel
from shk_cms.customers.models import Customer
from shk_cms.projects.models import Project


class Appointment(BaseModel):
    """
    Termine
    """
    APPOINTMENT_TYPES = [
        ('consultation', 'Beratung'),
        ('site_visit', 'Vor-Ort-Besichtigung'),
        ('installation', 'Installation'),
        ('maintenance', 'Wartung'),
        ('repair', 'Reparatur'),
        ('meeting', 'Besprechung'),
        ('phone_call', 'Telefonat'),
        ('other', 'Sonstiges'),
    ]
    
    APPOINTMENT_STATUS = [
        ('scheduled', 'Geplant'),
        ('confirmed', 'Bestätigt'),
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Abgeschlossen'),
        ('cancelled', 'Abgesagt'),
        ('no_show', 'Nicht erschienen'),
        ('rescheduled', 'Verschoben'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Niedrig'),
        ('medium', 'Mittel'),
        ('high', 'Hoch'),
        ('urgent', 'Dringend'),
    ]
    
    # Grunddaten
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='consultation')
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Zeitinformationen
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    # Verknüpfungen
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='appointments')
    
    # Zuweisungen
    assigned_employees = models.ManyToManyField(User, related_name='assigned_appointments', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_appointments')
    
    # Lokation
    location = models.TextField(blank=True, null=True)
    
    # Erinnerungen
    reminder_sent = models.BooleanField(default=False)
    reminder_datetime = models.DateTimeField(blank=True, null=True)
    
    # Zusätzliche Informationen
    internal_notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    
    # Fahrtzeit
    travel_time_to = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    travel_time_from = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Termin'
        verbose_name_plural = 'Termine'
        ordering = ['start_datetime']
        
    def __str__(self):
        return f"{self.title} - {self.customer} ({self.start_datetime.strftime('%d.%m.%Y %H:%M')})"
        
    def save(self, *args, **kwargs):
        """Automatische Berechnung der Dauer"""
        if self.start_datetime and self.end_datetime and not self.duration_hours:
            duration_delta = self.end_datetime - self.start_datetime
            self.duration_hours = round(duration_delta.total_seconds() / 3600, 2)
            
        super().save(*args, **kwargs)
        
    @property
    def is_past_due(self):
        """Prüft ob der Termin in der Vergangenheit liegt"""
        return self.end_datetime < timezone.now()
        
    @property
    def is_today(self):
        """Prüft ob der Termin heute ist"""
        return self.start_datetime.date() == date.today()
        
    @property
    def duration_formatted(self):
        """Formatierte Dauer (HH:MM)"""
        if self.duration_hours:
            hours = int(self.duration_hours)
            minutes = int((self.duration_hours - hours) * 60)
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"


class Calendar(BaseModel):
    """
    Kalender für Terminplanung
    """
    CALENDAR_TYPES = [
        ('personal', 'Persönlich'),
        ('team', 'Team'),
        ('company', 'Firma'),
        ('customer', 'Kunde'),
        ('project', 'Projekt'),
    ]
    
    # Grunddaten
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPES, default='personal')
    
    # Farbe für Anzeige
    color = models.CharField(max_length=7, default='#007bff')  # Hex-Farbcode
    
    # Zugriff
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_calendars')
    shared_with = models.ManyToManyField(User, through='CalendarPermission', related_name='shared_calendars')
    
    # Einstellungen
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Kalender'
        verbose_name_plural = 'Kalender'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class CalendarPermission(BaseModel):
    """
    Kalender-Berechtigungen
    """
    PERMISSION_LEVELS = [
        ('view', 'Anzeigen'),
        ('edit', 'Bearbeiten'),
        ('admin', 'Verwalten'),
    ]
    
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS, default='view')
    
    class Meta:
        verbose_name = 'Kalender-Berechtigung'
        verbose_name_plural = 'Kalender-Berechtigungen'
        unique_together = ['calendar', 'user']
        
    def __str__(self):
        return f"{self.calendar.name} - {self.user.get_full_name()} ({self.get_permission_level_display()})"


class RecurringAppointment(BaseModel):
    """
    Wiederkehrende Termine
    """
    RECURRENCE_TYPES = [
        ('daily', 'Täglich'),
        ('weekly', 'Wöchentlich'),
        ('monthly', 'Monatlich'),
        ('yearly', 'Jährlich'),
    ]
    
    # Grunddaten
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    appointment_type = models.CharField(max_length=20, choices=Appointment.APPOINTMENT_TYPES, default='consultation')
    
    # Verknüpfungen
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='recurring_appointments')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='recurring_appointments')
    
    # Wiederkehrende Einstellungen
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_TYPES, default='monthly')
    interval = models.IntegerField(default=1)  # Alle X Tage/Wochen/Monate
    
    # Zeitinformationen
    start_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    
    # Gültigkeitszeitraum
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    # Zuweisungen
    assigned_employees = models.ManyToManyField(User, related_name='assigned_recurring_appointments', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_recurring_appointments')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Zusätzliche Informationen
    location = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Wiederkehrender Termin'
        verbose_name_plural = 'Wiederkehrende Termine'
        ordering = ['start_date']
        
    def __str__(self):
        return f"{self.title} - {self.customer} ({self.get_recurrence_type_display()})"
        
    def generate_appointments(self, end_date=None):
        """Generiert einzelne Termine basierend auf der Wiederholungsregel"""
        from datetime import timedelta
        import calendar
        
        if not end_date:
            end_date = self.end_date or (self.start_date + timedelta(days=365))
            
        appointments = []
        current_date = self.start_date
        
        while current_date <= end_date:
            # Prüfen ob bereits ein Termin für dieses Datum existiert
            existing = Appointment.objects.filter(
                customer=self.customer,
                start_datetime__date=current_date,
                title=self.title
            ).exists()
            
            if not existing:
                start_datetime = timezone.make_aware(datetime.combine(current_date, self.start_time))
                end_datetime = start_datetime + timedelta(hours=float(self.duration_hours))
                
                appointment = Appointment.objects.create(
                    title=self.title,
                    description=self.description,
                    appointment_type=self.appointment_type,
                    customer=self.customer,
                    project=self.project,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    duration_hours=self.duration_hours,
                    location=self.location,
                    internal_notes=self.internal_notes,
                    created_by=self.created_by,
                    status='scheduled'
                )
                
                # Mitarbeiter zuweisen
                appointment.assigned_employees.set(self.assigned_employees.all())
                appointments.append(appointment)
            
            # Nächstes Datum berechnen
            if self.recurrence_type == 'daily':
                current_date += timedelta(days=self.interval)
            elif self.recurrence_type == 'weekly':
                current_date += timedelta(weeks=self.interval)
            elif self.recurrence_type == 'monthly':
                # Monatlich ist komplexer wegen unterschiedlicher Monatslängen
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_month = current_date.replace(month=current_date.month + self.interval)
                
                # Sicherstellen, dass das Datum gültig ist
                try:
                    current_date = next_month
                except ValueError:
                    # Datum existiert nicht (z.B. 31. Februar)
                    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
                    current_date = next_month.replace(day=min(current_date.day, last_day))
                    
            elif self.recurrence_type == 'yearly':
                current_date = current_date.replace(year=current_date.year + self.interval)
                
        return appointments


class AppointmentNote(BaseModel):
    """
    Terminnotizen
    """
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='notes')
    
    # Notizdetails
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Autor
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Sichtbarkeit
    is_internal = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Terminnotiz'
        verbose_name_plural = 'Terminnotizen'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.appointment.title} - {self.title}"