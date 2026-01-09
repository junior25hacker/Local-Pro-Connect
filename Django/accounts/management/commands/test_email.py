"""
Management command to test email configuration.
Usage: python manage.py test_email
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from accounts.email_utils import test_email_configuration


class Command(BaseCommand):
    help = 'Test email configuration and SMTP settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            default=settings.DEFAULT_FROM_EMAIL,
            help='Email address to send test email to (default: DEFAULT_FROM_EMAIL)',
        )

    def handle(self, *args, **options):
        recipient = options.get('recipient')
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('EMAIL CONFIGURATION TEST'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Display current configuration
        self.stdout.write('\nCurrent Email Configuration:')
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Testing Email Configuration...')
        self.stdout.write('='*60 + '\n')
        
        # Run email configuration test
        result = test_email_configuration()
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f"✓ {result['message']}"))
            self.stdout.write(self.style.SUCCESS("\nEmail configuration is working correctly!"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ {result['message']}"))
            self.stdout.write(self.style.ERROR("\nEmail configuration test failed."))
            self.stdout.write(self.style.ERROR("\nPlease check your settings:"))
            if 'error' in result['config']:
                self.stdout.write(f"Error: {result['config']['error']}")
        
        # Additional troubleshooting information
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Troubleshooting Information:')
        self.stdout.write('='*60)
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(self.style.WARNING(
                "\nⓘ Console Email Backend is being used (development mode)."
            ))
            self.stdout.write("  Emails will be printed to console instead of being sent.")
            self.stdout.write("\n  To enable real email sending, configure SMTP in .env:")
            self.stdout.write("    SMTP_PROVIDER=gmail")
            self.stdout.write("    EMAIL_HOST_USER=your-email@gmail.com")
            self.stdout.write("    EMAIL_HOST_PASSWORD=your-app-password")
        
        elif settings.EMAIL_HOST_USER == '':
            self.stdout.write(self.style.ERROR(
                "\n✗ EMAIL_HOST_USER is not configured!"
            ))
            self.stdout.write("  Please set EMAIL_HOST_USER in .env or Django settings")
        
        self.stdout.write('\n' + '='*60 + '\n')
