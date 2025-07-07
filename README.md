# SHK-Betriebs-CMS

## Übersicht

Modernes, webbasiertes CMS für Sanitär-, Heizungs- und Klimatechnik-Betriebe. Das System digitalisiert alle Geschäftsprozesse von der Kundenakquise bis zur Rechnungsstellung.

## 🚀 Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- Python 3.12+ (für lokale Entwicklung)
- Node.js 20+ (für Frontend-Entwicklung)

### Installation

1. **Repository klonen und Abhängigkeiten installieren:**
```bash
git clone <repository-url>
cd CMS

# Python Dependencies (in virtueller Umgebung empfohlen)
pip install -r requirements.txt

# Node.js Dependencies für Frontend (später)
# npm install
```

2. **Umgebungsvariablen konfigurieren:**
```bash
# .env ist bereits konfiguriert, bei Bedarf anpassen
cp .env.example .env  # Falls notwendig
```

3. **Datenbank starten:**
```bash
# PostgreSQL mit Docker starten
docker-compose up -d postgres

# Optional: pgAdmin für Datenbank-Management
docker-compose up -d pgadmin
```

4. **Django Migrations und Setup:**
```bash
# Datenbank-Migrationen erstellen und ausführen
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Static Files sammeln
python manage.py collectstatic
```

5. **Entwicklungsserver starten:**
```bash
# Django Backend (Port 8000)
python manage.py runserver

# Oder mit Docker
docker-compose up backend
```

### Zugriff auf die Anwendung

- **Django Admin:** http://localhost:8000/admin/
- **API Documentation:** http://localhost:8000/api/docs/
- **API Root:** http://localhost:8000/api/v1/
- **pgAdmin:** http://localhost:8080/ (admin@example.com / siehe .env)

## 📋 MVP Features (Phase 1)

### ✅ Implementiert

#### Backend (Django + DRF)
- ✅ **Projektstruktur** - Modulare Django Apps
- ✅ **Datenmodelle** - Alle MVP-Entitäten definiert
- ✅ **Admin Interface** - Vollständige Verwaltung
- ✅ **Basis-Konfiguration** - Settings, URLs, Apps

#### Module
- ✅ **Core** - Basis-Modelle (Address, ContactPerson, Company, Note)
- ✅ **Kundenverwaltung** - Customer, Adressen, Ansprechpartner, Interaktionen
- ✅ **Angebotswesen** - Quote, QuoteItem, QuoteDocument
- ✅ **Projektmanagement** - Project, Tasks, Team, Documents
- ✅ **Rechnungsstellung** - Invoice, InvoiceItem, Payment, Reminder
- ✅ **Personalverwaltung** - Employee, Skills, Documents, Availability
- ✅ **Zeiterfassung** - TimeEntry, Timesheet, WorkSchedule, OvertimeRequest
- ✅ **Terminplanung** - Appointment, Calendar, RecurringAppointment

### ✅ Phase 1 Komplett

- ✅ **Database Migrations** - Erstellt und getestet
- ✅ **REST API** - Serializers und ViewSets implementiert
- ✅ **Admin Interface** - Vollständig konfiguriert
- ✅ **Docker Setup** - Backend Container funktionsfähig

### 🔄 In Arbeit

- 🔄 **Angular Frontend** - Grundsetup mit Bootstrap
- 🔄 **Frontend-Backend Integration** - API-Verbindung

### 📅 Geplant

- 📅 **Authentication** - JWT Token Management
- 📅 **API Endpoints** - CRUD Operations für alle Entitäten
- 📅 **Frontend Components** - Angular Module und Services
- 📅 **Dashboard** - Übersicht und KPIs
- 📅 **PDF Generation** - Angebote und Rechnungen
- 📅 **File Upload** - Dokumente und Bilder
- 📅 **Email Integration** - Automatischer Versand

## 🗂️ Projektstruktur

```
SHK-CMS/
├── shk_cms/                    # Django Projekt
│   ├── core/                   # Kern-Funktionalität
│   ├── customers/              # Kundenverwaltung
│   ├── quotes/                 # Angebotswesen
│   ├── projects/               # Projektmanagement
│   ├── invoices/               # Rechnungsstellung
│   ├── employees/              # Personalverwaltung
│   ├── timetracking/           # Zeiterfassung
│   ├── schedules/              # Terminplanung
│   └── api/                    # REST API
├── frontend/                   # Angular Frontend (geplant)
├── docker-compose.yml          # Docker Services
├── Dockerfile                  # Django Container
├── requirements.txt            # Python Dependencies
├── .env                        # Umgebungsvariablen
└── README.md                   # Dokumentation
```

## 🔧 Entwicklung

### Django Commands

```bash
# Neue Migration erstellen
python manage.py makemigrations

# Migrationen ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Development Server
python manage.py runserver

# Shell öffnen
python manage.py shell

# Tests ausführen
python manage.py test
```

### Docker Commands

```bash
# Alle Services starten
docker-compose up -d

# Nur Datenbank
docker-compose up -d postgres

# Backend neu bauen
docker-compose build backend

# Logs anzeigen
docker-compose logs -f backend

# Services stoppen
docker-compose down
```

### Code Quality

```bash
# Code formatieren
black .

# Import sortieren
isort .

# Linting
flake8

# Tests mit Coverage
pytest --cov=shk_cms
```

## 📊 Datenmodell

### Kern-Entitäten

- **Customer** - Kunden (Privat/Geschäft) mit Adressen und Kontakten
- **Quote** - Angebote mit Positionen und Dokumenten
- **Project** - Projekte/Aufträge mit Tasks und Team
- **Invoice** - Rechnungen mit Positionen und Zahlungen
- **Employee** - Mitarbeiter mit Skills und Verfügbarkeit
- **TimeEntry** - Zeiterfassung mit Projekt- und Kundenbezug
- **Appointment** - Termine mit Wiederholung und Notizen

### Beziehungen

- Customer → Quotes → Projects → Invoices
- Projects → Tasks, TimeEntries, Appointments
- Employees → TimeEntries, Appointments, Projects

## 🔐 Sicherheit

- JWT-basierte Authentifizierung
- CORS-Konfiguration für Frontend
- CSRF-Schutz aktiviert
- Umgebungsvariablen für sensible Daten
- SQL Injection Schutz durch Django ORM

## 📈 Roadmap

### Phase 1 (MVP) - Q1 2025
- ✅ Backend-Grundstruktur
- 🔄 REST API
- 🔄 Angular Frontend
- 📅 Basis-Funktionalitäten

### Phase 2 - Q2 2025
- 📅 Erweiterte Projektplanung
- 📅 Material-/Lagerverwaltung
- 📅 Mobile App
- 📅 Wartungsverträge

### Phase 3 - Q3 2025
- 📅 DATEV-Integration
- 📅 Dokumentenmanagement
- 📅 Business Intelligence
- 📅 Branchenintegrationen

## 🤝 Beitragen

1. Feature Branch erstellen
2. Änderungen implementieren
3. Tests hinzufügen/aktualisieren
4. Pull Request erstellen

## 📄 Lizenz

Proprietäre Software - Alle Rechte vorbehalten

## 📞 Support

Bei Fragen oder Problemen:
- Issue im Repository erstellen
- Dokumentation in CLAUDE.md prüfen
- Development Team kontaktieren

---

**Status:** 🚧 In aktiver Entwicklung
**Version:** 1.0.0-alpha
**Letzte Aktualisierung:** 2025-01-06