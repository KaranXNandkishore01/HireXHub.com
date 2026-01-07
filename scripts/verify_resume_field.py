import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from users.models import UserProfile
try:
    field = UserProfile._meta.get_field('resume')
    print("Resume field exists.")
except Exception as e:
    print(f"Error: {e}")
