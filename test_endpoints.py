#!/usr/bin/env python
"""
Test script to verify API endpoints are working
"""
import requests
import json
from requests.auth import HTTPBasicAuth

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n--- Testing {method} {url} ---")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        return response.status_code, response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, str(e)

def main():
    print("Testing SHK-CMS API Endpoints")
    print("=" * 50)
    
    # Test main API endpoints
    endpoints_to_test = [
        "/",
        "/timetracking/",
        "/timetracking/entries/",
        "/timetracking/timesheets/",
        "/timetracking/schedules/",
        "/timetracking/overtime-requests/",
        "/schedules/",
        "/schedules/appointments/",
        "/schedules/calendars/",
        "/schedules/permissions/",
        "/schedules/recurring/",
        "/schedules/notes/",
        
        # Custom actions
        "/timetracking/entries/my_entries/",
        "/timetracking/entries/today/",
        "/timetracking/timesheets/pending_approval/",
        "/timetracking/schedules/today/",
        "/timetracking/schedules/week/",
        "/timetracking/overtime-requests/pending/",
        "/schedules/appointments/today/",
        "/schedules/appointments/week/",
        "/schedules/appointments/my_appointments/",
        "/schedules/appointments/upcoming/",
        "/schedules/appointments/calendar_view/",
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        status_code, response = test_endpoint(endpoint)
        results[endpoint] = {
            'status_code': status_code,
            'response_preview': response[:100] if response else None
        }
    
    print("\n\n=== SUMMARY ===")
    print(f"{'Endpoint':<50} {'Status':<10} {'Response Preview'}")
    print("-" * 80)
    
    for endpoint, result in results.items():
        status = result['status_code'] if result['status_code'] else 'ERROR'
        preview = result['response_preview'] if result['response_preview'] else 'No response'
        print(f"{endpoint:<50} {status:<10} {preview}")

if __name__ == "__main__":
    main()