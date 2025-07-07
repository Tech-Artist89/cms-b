# SHK-CMS API Endpoints Summary

## Base URL
All API endpoints are prefixed with: `http://localhost:8000/api/v1/`

## Authentication
All endpoints require authentication. Unauthenticated requests return:
- **Status Code**: 401 (Unauthorized)
- **Response**: `{"detail":"Anmeldedaten fehlen."}`

## Timetracking Module (`/api/v1/timetracking/`)

### Time Entries (`/api/v1/timetracking/entries/`)
- **GET** `/api/v1/timetracking/entries/` - List all time entries
- **POST** `/api/v1/timetracking/entries/` - Create new time entry
- **GET** `/api/v1/timetracking/entries/{id}/` - Get specific time entry
- **PUT** `/api/v1/timetracking/entries/{id}/` - Update time entry
- **DELETE** `/api/v1/timetracking/entries/{id}/` - Delete time entry

#### Custom Actions:
- **GET** `/api/v1/timetracking/entries/my_entries/` - Current user's time entries
- **GET** `/api/v1/timetracking/entries/today/` - Today's time entries
- **POST** `/api/v1/timetracking/entries/bulk_create/` - Bulk create time entries

### Timesheets (`/api/v1/timetracking/timesheets/`)
- **GET** `/api/v1/timetracking/timesheets/` - List all timesheets
- **POST** `/api/v1/timetracking/timesheets/` - Create new timesheet
- **GET** `/api/v1/timetracking/timesheets/{id}/` - Get specific timesheet
- **PUT** `/api/v1/timetracking/timesheets/{id}/` - Update timesheet
- **DELETE** `/api/v1/timetracking/timesheets/{id}/` - Delete timesheet

#### Custom Actions:
- **GET** `/api/v1/timetracking/timesheets/pending_approval/` - Timesheets pending approval
- **POST** `/api/v1/timetracking/timesheets/{id}/approve/` - Approve/reject timesheet

### Work Schedules (`/api/v1/timetracking/schedules/`)
- **GET** `/api/v1/timetracking/schedules/` - List all work schedules
- **POST** `/api/v1/timetracking/schedules/` - Create new work schedule
- **GET** `/api/v1/timetracking/schedules/{id}/` - Get specific work schedule
- **PUT** `/api/v1/timetracking/schedules/{id}/` - Update work schedule
- **DELETE** `/api/v1/timetracking/schedules/{id}/` - Delete work schedule

#### Custom Actions:
- **GET** `/api/v1/timetracking/schedules/today/` - Today's work schedules
- **GET** `/api/v1/timetracking/schedules/week/` - Current week's schedules

### Overtime Requests (`/api/v1/timetracking/overtime-requests/`)
- **GET** `/api/v1/timetracking/overtime-requests/` - List all overtime requests
- **POST** `/api/v1/timetracking/overtime-requests/` - Create new overtime request
- **GET** `/api/v1/timetracking/overtime-requests/{id}/` - Get specific overtime request
- **PUT** `/api/v1/timetracking/overtime-requests/{id}/` - Update overtime request
- **DELETE** `/api/v1/timetracking/overtime-requests/{id}/` - Delete overtime request

#### Custom Actions:
- **GET** `/api/v1/timetracking/overtime-requests/pending/` - Pending overtime requests

## Schedules Module (`/api/v1/schedules/`)

### Appointments (`/api/v1/schedules/appointments/`)
- **GET** `/api/v1/schedules/appointments/` - List all appointments
- **POST** `/api/v1/schedules/appointments/` - Create new appointment
- **GET** `/api/v1/schedules/appointments/{id}/` - Get specific appointment
- **PUT** `/api/v1/schedules/appointments/{id}/` - Update appointment
- **DELETE** `/api/v1/schedules/appointments/{id}/` - Delete appointment

#### Custom Actions:
- **GET** `/api/v1/schedules/appointments/today/` - Today's appointments
- **GET** `/api/v1/schedules/appointments/week/` - Current week's appointments
- **GET** `/api/v1/schedules/appointments/my_appointments/` - Current user's appointments
- **GET** `/api/v1/schedules/appointments/upcoming/` - Upcoming appointments (next 7 days)
- **GET** `/api/v1/schedules/appointments/calendar_view/` - Calendar view (requires start_date and end_date params)
- **POST** `/api/v1/schedules/appointments/bulk_update/` - Bulk update appointments

### Calendars (`/api/v1/schedules/calendars/`)
- **GET** `/api/v1/schedules/calendars/` - List all calendars
- **POST** `/api/v1/schedules/calendars/` - Create new calendar
- **GET** `/api/v1/schedules/calendars/{id}/` - Get specific calendar
- **PUT** `/api/v1/schedules/calendars/{id}/` - Update calendar
- **DELETE** `/api/v1/schedules/calendars/{id}/` - Delete calendar

### Calendar Permissions (`/api/v1/schedules/permissions/`)
- **GET** `/api/v1/schedules/permissions/` - List all calendar permissions
- **POST** `/api/v1/schedules/permissions/` - Create new calendar permission
- **GET** `/api/v1/schedules/permissions/{id}/` - Get specific calendar permission
- **PUT** `/api/v1/schedules/permissions/{id}/` - Update calendar permission
- **DELETE** `/api/v1/schedules/permissions/{id}/` - Delete calendar permission

### Recurring Appointments (`/api/v1/schedules/recurring/`)
- **GET** `/api/v1/schedules/recurring/` - List all recurring appointments
- **POST** `/api/v1/schedules/recurring/` - Create new recurring appointment
- **GET** `/api/v1/schedules/recurring/{id}/` - Get specific recurring appointment
- **PUT** `/api/v1/schedules/recurring/{id}/` - Update recurring appointment
- **DELETE** `/api/v1/schedules/recurring/{id}/` - Delete recurring appointment

#### Custom Actions:
- **POST** `/api/v1/schedules/recurring/{id}/generate_appointments/` - Generate appointments from recurring pattern

### Appointment Notes (`/api/v1/schedules/notes/`)
- **GET** `/api/v1/schedules/notes/` - List all appointment notes
- **POST** `/api/v1/schedules/notes/` - Create new appointment note
- **GET** `/api/v1/schedules/notes/{id}/` - Get specific appointment note
- **PUT** `/api/v1/schedules/notes/{id}/` - Update appointment note
- **DELETE** `/api/v1/schedules/notes/{id}/` - Delete appointment note

## Error Responses

### 401 Unauthorized
When authentication is missing or invalid:
```json
{"detail":"Anmeldedaten fehlen."}
```

### 404 Not Found
When an endpoint doesn't exist:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title>Page not found at /api/v1/wrong-endpoint/</title>
  ...
</head>
```

### 405 Method Not Allowed
When using an unsupported HTTP method on an endpoint, you'll get a 405 error.

## Frontend Integration Notes

1. **Base URL**: Use `http://localhost:8000/api/v1/` for all API calls
2. **Authentication**: All endpoints require authentication headers
3. **Content-Type**: Use `application/json` for POST/PUT requests
4. **URL Structure**: Follow the exact patterns above - case-sensitive
5. **Custom Actions**: Use the custom action endpoints for specialized queries (e.g., `today`, `week`, `my_appointments`)

## Common Issues and Solutions

1. **404 Errors**: Check URL spelling and ensure exact path matches
2. **405 Errors**: Verify HTTP method is supported for the endpoint
3. **401 Errors**: Add proper authentication headers
4. **CORS Errors**: Ensure frontend is configured to handle CORS if needed