# SHK-CMS REST API Dokumentation

## Übersicht

Die SHK-CMS REST API bietet vollständigen Zugriff auf alle Funktionen des Content Management Systems. Die API basiert auf Django REST Framework und folgt RESTful-Prinzipien.

## Basis-URLs

- **Development:** `http://localhost:8000/api/v1/`
- **API Documentation:** `http://localhost:8000/api/docs/`
- **Admin Interface:** `http://localhost:8000/admin/`

## Authentifizierung

Die API verwendet JWT (JSON Web Tokens) für die Authentifizierung.

### Token erhalten
```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token verwenden
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## API Endpoints

### 🔐 Authentication & Core
- **Base URL:** `/api/v1/auth/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/token/` | POST | JWT Token erhalten |
| `/token/refresh/` | POST | Token erneuern |
| `/token/verify/` | POST | Token validieren |
| `/addresses/` | GET, POST | Adressen verwalten |
| `/contacts/` | GET, POST | Ansprechpartner verwalten |
| `/companies/` | GET, POST | Firmen verwalten |
| `/notes/` | GET, POST | Notizen verwalten |

### 👥 Kundenverwaltung (CRM)
- **Base URL:** `/api/v1/customers/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/customers/` | GET, POST | Kunden auflisten/erstellen |
| `/customers/{id}/` | GET, PUT, PATCH, DELETE | Kunde details |
| `/customers/{id}/interactions/` | GET | Kundeninteraktionen |
| `/customers/{id}/add_interaction/` | POST | Interaktion hinzufügen |
| `/customers/stats/` | GET | Kunden-Statistiken |
| `/addresses/` | GET, POST | Kundenadressen |
| `/contacts/` | GET, POST | Kundenkontakte |
| `/interactions/` | GET, POST | Alle Interaktionen |
| `/interactions/follow_ups/` | GET | Follow-up Interaktionen |

### 💰 Angebotswesen
- **Base URL:** `/api/v1/quotes/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/quotes/` | GET, POST | Angebote auflisten/erstellen |
| `/quotes/{id}/` | GET, PUT, PATCH, DELETE | Angebot details |
| `/quotes/{id}/duplicate/` | POST | Angebot duplizieren |
| `/quotes/{id}/send/` | POST | Angebot versenden |
| `/quotes/{id}/accept/` | POST | Angebot annehmen |
| `/quotes/{id}/reject/` | POST | Angebot ablehnen |
| `/quotes/stats/` | GET | Angebots-Statistiken |
| `/quotes/expiring_soon/` | GET | Bald ablaufende Angebote |
| `/items/` | GET, POST | Angebotspositionen |
| `/documents/` | GET, POST | Angebotsdokumente |

### 🏗️ Projektmanagement
- **Base URL:** `/api/v1/projects/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/projects/` | GET, POST | Projekte auflisten/erstellen |
| `/projects/{id}/` | GET, PUT, PATCH, DELETE | Projekt details |
| `/projects/{id}/tasks/` | GET | Projektaufgaben |
| `/projects/{id}/add_task/` | POST | Aufgabe hinzufügen |
| `/projects/{id}/update_progress/` | POST | Fortschritt aktualisieren |
| `/projects/stats/` | GET | Projekt-Statistiken |
| `/projects/my_projects/` | GET | Meine Projekte |
| `/projects/overdue/` | GET | Überfällige Projekte |
| `/team-members/` | GET, POST | Teammitglieder |
| `/tasks/` | GET, POST | Alle Aufgaben |
| `/tasks/{id}/complete/` | POST | Aufgabe abschließen |
| `/tasks/my_tasks/` | GET | Meine Aufgaben |
| `/tasks/overdue/` | GET | Überfällige Aufgaben |
| `/documents/` | GET, POST | Projektdokumente |

### 🧾 Rechnungsstellung
- **Base URL:** `/api/v1/invoices/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/invoices/` | GET, POST | Rechnungen auflisten/erstellen |
| `/invoices/{id}/` | GET, PUT, PATCH, DELETE | Rechnung details |
| `/invoices/stats/` | GET | Rechnungs-Statistiken |
| `/invoices/overdue/` | GET | Überfällige Rechnungen |
| `/items/` | GET, POST | Rechnungspositionen |
| `/payments/` | GET, POST | Zahlungen |
| `/reminders/` | GET, POST | Mahnungen |

### 👷 Personalverwaltung
- **Base URL:** `/api/v1/employees/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/users/` | GET | Benutzer auflisten |
| `/employees/` | GET, POST | Mitarbeiter auflisten/erstellen |
| `/employees/{id}/` | GET, PUT, PATCH, DELETE | Mitarbeiter details |
| `/employees/stats/` | GET | Personal-Statistiken |
| `/employees/active/` | GET | Aktive Mitarbeiter |
| `/skills/` | GET, POST | Mitarbeiterfähigkeiten |
| `/documents/` | GET, POST | Mitarbeiterdokumente |
| `/availability/` | GET, POST | Verfügbarkeit |
| `/availability/pending_approval/` | GET | Genehmigungen ausstehend |

### ⏰ Zeiterfassung
- **Base URL:** `/api/v1/timetracking/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/entries/` | GET, POST | Zeiteinträge auflisten/erstellen |
| `/entries/my_entries/` | GET | Meine Zeiteinträge |
| `/entries/today/` | GET | Heutige Einträge |
| `/entries/bulk_create/` | POST | Mehrere Einträge erstellen |
| `/timesheets/` | GET, POST | Stundenzettel |
| `/timesheets/{id}/approve/` | POST | Stundenzettel genehmigen |
| `/timesheets/pending_approval/` | GET | Genehmigungen ausstehend |
| `/schedules/` | GET, POST | Arbeitspläne |
| `/schedules/today/` | GET | Heutiger Arbeitsplan |
| `/schedules/week/` | GET | Wöchentlicher Plan |
| `/overtime-requests/` | GET, POST | Überstunden-Anfragen |
| `/overtime-requests/pending/` | GET | Ausstehende Anfragen |

### 📅 Terminplanung
- **Base URL:** `/api/v1/schedules/`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/appointments/` | GET, POST | Termine auflisten/erstellen |
| `/appointments/{id}/` | GET, PUT, PATCH, DELETE | Termin details |
| `/appointments/today/` | GET | Heutige Termine |
| `/appointments/week/` | GET | Wöchentliche Termine |
| `/appointments/my_appointments/` | GET | Meine Termine |
| `/appointments/upcoming/` | GET | Bevorstehende Termine |
| `/appointments/calendar_view/` | GET | Kalenderansicht |
| `/appointments/bulk_update/` | POST | Mehrere Termine bearbeiten |
| `/calendars/` | GET, POST | Kalender verwalten |
| `/permissions/` | GET, POST | Kalender-Berechtigungen |
| `/recurring/` | GET, POST | Wiederkehrende Termine |
| `/recurring/{id}/generate_appointments/` | POST | Termine generieren |
| `/notes/` | GET, POST | Terminnotizen |

## Häufige Parameter

### Filterung
Die meisten Endpoints unterstützen Filterung:
```http
GET /api/v1/customers/customers/?customer_type=business&is_active=true
```

### Suche
Volltextsuche in relevanten Feldern:
```http
GET /api/v1/customers/customers/?search=Müller
```

### Sortierung
```http
GET /api/v1/quotes/quotes/?ordering=-created_at
```

### Paginierung
```http
GET /api/v1/projects/projects/?page=2&page_size=25
```

## Datenformate

### Datumsformate
- **Datum:** `YYYY-MM-DD` (z.B. `2025-01-06`)
- **Datum/Zeit:** `YYYY-MM-DDTHH:MM:SS` (z.B. `2025-01-06T14:30:00`)

### Dezimalzahlen
- **Preise:** Bis zu 10 Stellen, 2 Nachkommastellen
- **Stunden:** Bis zu 5 Stellen, 2 Nachkommastellen

## Beispiel-Requests

### Kunde erstellen
```http
POST /api/v1/customers/customers/
Content-Type: application/json
Authorization: Bearer {token}

{
    "customer_type": "private",
    "category": "B",
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max@example.com",
    "phone": "+49 123 456789"
}
```

### Angebot mit Positionen erstellen
```http
POST /api/v1/quotes/quotes/
Content-Type: application/json
Authorization: Bearer {token}

{
    "customer": "customer-uuid",
    "title": "Heizungsmodernisierung",
    "description": "Kompletterneuerung der Heizungsanlage",
    "valid_until": "2025-02-06",
    "items": [
        {
            "position_number": 1,
            "title": "Gasbrennwerttherme",
            "quantity": 1,
            "unit": "Stück",
            "unit_price": 2500.00
        },
        {
            "position_number": 2,
            "title": "Installation und Inbetriebnahme",
            "quantity": 8,
            "unit": "Stunden",
            "unit_price": 75.00
        }
    ]
}
```

### Termin erstellen
```http
POST /api/v1/schedules/appointments/
Content-Type: application/json
Authorization: Bearer {token}

{
    "title": "Vor-Ort Besichtigung",
    "appointment_type": "site_visit",
    "customer": "customer-uuid",
    "start_datetime": "2025-01-08T14:00:00",
    "end_datetime": "2025-01-08T15:00:00",
    "location": "Musterstraße 123, 12345 Musterstadt",
    "assigned_employees": ["employee-uuid"]
}
```

## Fehler-Codes

| Code | Beschreibung |
|------|--------------|
| 200 | OK - Erfolgreiche Anfrage |
| 201 | Created - Ressource erstellt |
| 400 | Bad Request - Ungültige Daten |
| 401 | Unauthorized - Authentifizierung erforderlich |
| 403 | Forbidden - Keine Berechtigung |
| 404 | Not Found - Ressource nicht gefunden |
| 500 | Internal Server Error - Serverfehler |

## Rate Limiting

Aktuell kein Rate Limiting implementiert. In Produktion empfohlen: 1000 Requests/Stunde pro Benutzer.

## Versionierung

Aktuelle Version: **v1**
Basis-URL: `/api/v1/`

Änderungen werden über neue Versionen eingeführt (v2, v3, etc.).

---

**Letzte Aktualisierung:** 2025-01-06
**API Version:** 1.0.0