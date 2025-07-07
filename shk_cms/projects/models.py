"""
Project Models für SHK-CMS

Modelle für Auftragsabwicklung und Projektmanagement
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from shk_cms.core.models import BaseModel
from shk_cms.customers.models import Customer
from shk_cms.quotes.models import Quote


class Project(BaseModel):
    """
    Projekt/Auftrag
    """
    PROJECT_STATUS = [
        ('planning', 'Planung'),
        ('approved', 'Genehmigt'),
        ('in_progress', 'In Bearbeitung'),
        ('on_hold', 'Pausiert'),
        ('completed', 'Abgeschlossen'),
        ('cancelled', 'Abgebrochen'),
        ('invoiced', 'Abgerechnet'),
    ]
    
    PROJECT_TYPES = [
        ('installation', 'Installation'),
        ('maintenance', 'Wartung'),
        ('repair', 'Reparatur'),
        ('modernization', 'Modernisierung'),
        ('emergency', 'Notfall'),
        ('consultation', 'Beratung'),
    ]
    
    # Grunddaten
    project_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, blank=True, null=True, related_name='projects')
    
    # Projektdetails
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, default='installation')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    
    # Termine
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    
    # Budgetinformationen
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Zuweisungen
    project_manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(
        User, 
        through='ProjectTeamMember',
        related_name='assigned_projects'
    )
    
    # Status-Tracking
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Zusätzliche Informationen
    internal_notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Projekt'
        verbose_name_plural = 'Projekte'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Projekt {self.project_number} - {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Generierung der Projektnummer"""
        if not self.project_number:
            # Einfache Projektnummer-Generierung
            from datetime import date
            today = date.today()
            year = today.year
            
            last_project = Project.objects.filter(
                project_number__startswith=f'P{year}'
            ).order_by('-project_number').first()
            
            if last_project:
                try:
                    last_number = int(last_project.project_number[5:])
                    self.project_number = f"P{year}{last_number + 1:04d}"
                except (ValueError, TypeError):
                    self.project_number = f"P{year}0001"
            else:
                self.project_number = f"P{year}0001"
                
        super().save(*args, **kwargs)
        
    @property
    def is_overdue(self):
        """Prüft ob das Projekt überfällig ist"""
        from datetime import date
        return self.deadline and self.deadline < date.today() and self.status not in ['completed', 'cancelled', 'invoiced']
        
    @property
    def budget_utilization(self):
        """Budgetausnutzung in Prozent"""
        if self.budget_amount > 0:
            return (self.actual_cost / self.budget_amount) * 100
        return 0


class ProjectTeamMember(BaseModel):
    """
    Projektteam-Mitgliedschaften
    """
    ROLES = [
        ('manager', 'Projektleiter'),
        ('technician', 'Techniker'),
        ('apprentice', 'Azubi'),
        ('consultant', 'Berater'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='technician')
    
    # Zeitraum der Zuordnung
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Projektteam-Mitglied'
        verbose_name_plural = 'Projektteam-Mitglieder'
        unique_together = ['project', 'user']
        
    def __str__(self):
        return f"{self.project.project_number} - {self.user.get_full_name()} ({self.get_role_display()})"


class ProjectTask(BaseModel):
    """
    Projektaufgaben (To-Do-Liste)
    """
    TASK_STATUS = [
        ('pending', 'Offen'),
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Erledigt'),
        ('cancelled', 'Abgebrochen'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Niedrig'),
        ('medium', 'Mittel'),
        ('high', 'Hoch'),
        ('urgent', 'Dringend'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    
    # Aufgabendetails
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Termine
    due_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # Zuweisungen
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Fortschritt
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = 'Projektaufgabe'
        verbose_name_plural = 'Projektaufgaben'
        ordering = ['-priority', 'due_date']
        
    def __str__(self):
        return f"{self.project.project_number} - {self.title}"
        
    @property
    def is_overdue(self):
        """Prüft ob die Aufgabe überfällig ist"""
        from datetime import datetime
        return (self.due_date and self.due_date < datetime.now() and 
                self.status not in ['completed', 'cancelled'])


class ProjectDocument(BaseModel):
    """
    Projektdokumente
    """
    DOCUMENT_TYPES = [
        ('contract', 'Vertrag'),
        ('technical_drawing', 'Technische Zeichnung'),
        ('photo', 'Foto'),
        ('report', 'Bericht'),
        ('invoice', 'Rechnung'),
        ('certificate', 'Zertifikat'),
        ('manual', 'Handbuch'),
        ('other', 'Sonstiges'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='projects/documents/')
    description = models.TextField(blank=True, null=True)
    
    # Metadaten
    file_size = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Projektdokument'
        verbose_name_plural = 'Projektdokumente'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.project.project_number} - {self.title}"
        
    def save(self, *args, **kwargs):
        """Automatische Bestimmung der Dateigröße"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)