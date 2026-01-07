import sys
import os

with open('status.txt', 'w') as f:
    try:
        import allauth
        f.write("SUCCESS: allauth is installed.\n")
    except ImportError as e:
        f.write(f"ERROR: {e}\n")

    try:
        # We need to set DJANGO_SETTINGS_MODULE to import settings usually, 
        # but just importing the file as a module might work if path is right.
        # Better to use os.environ
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
        import django
        django.setup()
        f.write("SUCCESS: django.setup() passed.\n")
    except Exception as e:
        f.write(f"ERROR: django setup failed: {e}\n")
