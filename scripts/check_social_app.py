import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("--- DIAGNOSTIC REPORT ---")

# Check Sites
current_site_id = getattr(settings, 'SITE_ID', 1)
try:
    current_site = Site.objects.get(pk=current_site_id)
    print(f"Current SITE_ID: {current_site_id}")
    print(f"Current Site Domain: {current_site.domain}")
    print(f"Current Site Name: {current_site.name}")
except Site.DoesNotExist:
    print(f"ERROR: No Site found with ID {current_site_id}")

# Check Social Apps
google_apps = SocialApp.objects.filter(provider='google')
if google_apps.exists():
    print(f"Found {google_apps.count()} Google SocialApp(s).")
    for app in google_apps:
        print(f"- App Name: {app.name}")
        print(f"  - Client ID: {app.client_id[:5]}... (truncated)")
        print(f"  - Sites attached: {[s.id for s in app.sites.all()]}")
        
        if current_site_id in [s.id for s in app.sites.all()]:
            print("  -> OK: Attached to current site.")
        else:
            print("  -> ERROR: NOT attached to current site.")
else:
    print("ERROR: No Google SocialApp found in database.")

print("-------------------------")
