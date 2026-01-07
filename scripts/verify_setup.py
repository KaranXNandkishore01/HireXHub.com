import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from users.models import User
from recruitment.models import Company, JobListing
from recruitment.utils.ranker import Ranker

def verify():
    print("Verifying setup...")
    
    # Check User Model
    if not User.objects.filter(username='test_hr').exists():
        user = User.objects.create_user(username='test_hr', password='password123', is_hr=True)
        print("Created HR User.")
    else:
        print("HR User exists.")

    # Check Ranker Import
    try:
        ranker = Ranker()
        print("Ranker initialized successfully.")
    except Exception as e:
        print(f"Ranker initialization failed: {e}")

    print("Verification complete. You can now run 'python manage.py runserver'.")

if __name__ == '__main__':
    verify()
