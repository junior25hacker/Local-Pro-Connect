import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail, get_connection
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

def mask_credential(cred):
    if not cred:
        return "Not Set"
    if len(cred) > 4:
        return f"{cred[:2]}...{cred[-2:]}"
    return "***"

def test_email_config():
    print("=" * 60)
    print(f"EMAIL DIAGNOSTIC - {datetime.now()}")
    print("=" * 60)

    # 1. Check Settings
    print(f"\n[1] Configuration Check:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"EMAIL_HOST_USER: {mask_credential(settings.EMAIL_HOST_USER)}")
    print(f"EMAIL_HOST_PASSWORD: {'Set' if settings.EMAIL_HOST_PASSWORD else 'Not Set'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # 2. Check for Console Backend Warning
    if 'console.EmailBackend' in settings.EMAIL_BACKEND:
        print("\n[WARNING] You are using the Console Email Backend!")
        print("Emails will NOT be sent to real addresses. They will appear here in the console.")
        print("To fix this, ensure EMAIL_HOST_USER is set in your .env file.")
        
    # 3. Connectivity Test
    print(f"\n[2] Connectivity Test:")
    if not settings.EMAIL_HOST_USER:
        print("SKIPPING: No email user configured to test with.")
        return

    try:
        print(f"Attempting to connect to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        connection = get_connection()
        connection.open()
        print("SUCCESS: Connected to SMTP server.")
        connection.close()
    except Exception as e:
        print(f"FAILED: Could not connect to SMTP server.")
        print(f"Error: {str(e)}")
        return

    # 4. Sending Test
    print(f"\n[3] Sending Test:")
    try:
        print(f"Sending test email to {settings.EMAIL_HOST_USER}...")
        send_mail(
            subject=f'Test Email from LocaPro - {datetime.now()}',
            message='If you see this, your email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print("SUCCESS: Email sent successfully! Check your inbox.")
    except Exception as e:
        print(f"FAILED: Error sending email.")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_email_config()
