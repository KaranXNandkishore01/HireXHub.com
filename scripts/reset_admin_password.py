import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

def reset_admin():
    User = get_user_model()
    
    print("--- Existing Superusers ---")
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        for su in superusers:
            print(f"- Username: {su.username}, Email: {su.email}")
    else:
        print("No superusers found.")

    print("\n--- Resetting Password ---")
    username = 'admin'
    new_password = 'admin123'
    
    try:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.email = 'admin@example.com'
            user.is_staff = True
            user.is_superuser = True
            print(f"Created new superuser '{username}'.")
        else:
            print(f"Found existing user '{username}'.")
            # Ensure privileges
            user.is_staff = True
            user.is_superuser = True

        user.set_password(new_password)
        user.save()
        print(f"Password for '{username}' has been set to: {new_password}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    reset_admin()
