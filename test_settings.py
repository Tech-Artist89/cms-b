#!/usr/bin/env python3
"""
Simple test to validate Django settings syntax
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test if we can import our settings
    import shk_cms.settings as settings
    print("✓ Settings imported successfully")
    
    # Check if required variables are present
    required_settings = [
        'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'INSTALLED_APPS',
        'MIDDLEWARE', 'ROOT_URLCONF', 'DATABASES', 'REST_FRAMEWORK'
    ]
    
    for setting in required_settings:
        if hasattr(settings, setting):
            print(f"✓ {setting} is configured")
        else:
            print(f"✗ {setting} is missing")
    
    # Check apps configuration
    print(f"✓ Total installed apps: {len(settings.INSTALLED_APPS)}")
    
    local_apps = [app for app in settings.INSTALLED_APPS if app.startswith('shk_cms')]
    print(f"✓ Local apps: {local_apps}")
    
except ImportError as e:
    print(f"✗ Error importing settings: {e}")
except Exception as e:
    print(f"✗ Error in settings: {e}")

print("\nTesting decouple configuration...")
try:
    from decouple import config
    print("✓ python-decouple is available")
    
    # Test config loading (with defaults)
    debug = config('DEBUG', default=True, cast=bool)
    print(f"✓ DEBUG setting: {debug}")
    
except ImportError:
    print("✗ python-decouple not available")
except Exception as e:
    print(f"✗ Error with decouple: {e}")

print("\nDone!")