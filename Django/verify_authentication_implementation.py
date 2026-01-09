#!/usr/bin/env python
"""
Verification script for Authentication, Session Management, and RBAC implementation.
Checks that all components are properly installed and configured.

Usage: python verify_authentication_implementation.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")


def print_check(name, status, details=""):
    if status:
        print(f"{GREEN}✓{RESET} {name}")
    else:
        print(f"{RED}✗{RESET} {name}")
    if details:
        print(f"  {details}")


def verify_files():
    """Verify all required files exist."""
    print_header("FILE VERIFICATION")
    
    required_files = {
        'Core Implementation': [
            'accounts/decorators.py',
            'accounts/email_utils.py',
            'accounts/management/commands/test_email.py',
        ],
        'Templates': [
            'requests/templates/requests/provider_dashboard.html',
            'requests/templates/emails/profile_update_email.txt',
            'requests/templates/emails/profile_update_email.html',
        ],
        'Documentation': [
            'AUTHENTICATION_RBAC_DOCUMENTATION.md',
            'QUICK_START_AUTH_TESTING.md',
            'IMPLEMENTATION_SUMMARY.md',
        ],
    }
    
    all_exist = True
    for category, files in required_files.items():
        print(f"{BOLD}{category}:{RESET}")
        for filepath in files:
            full_path = Path(filepath)
            exists = full_path.exists()
            print_check(f"  {filepath}", exists)
            if not exists:
                all_exist = False
    
    return all_exist


def verify_imports():
    """Verify all modules can be imported."""
    print_header("IMPORT VERIFICATION")
    
    imports_to_test = {
        'Decorators': 'from accounts.decorators import login_required, provider_required, owner_required, read_only_profile',
        'Email Utils': 'from accounts.email_utils import send_profile_update_email, test_email_configuration',
        'Models': 'from accounts.models import ProviderProfile, UserProfile',
        'Views': 'from accounts.views import provider_dashboard, edit_provider_profile',
    }
    
    all_imported = True
    for name, import_statement in imports_to_test.items():
        try:
            exec(import_statement)
            print_check(name, True)
        except ImportError as e:
            print_check(name, False, str(e))
            all_imported = False
    
    return all_imported


def verify_settings():
    """Verify Django settings are configured."""
    print_header("SETTINGS VERIFICATION")
    
    settings_to_check = {
        'Session Engine': {
            'setting': settings.SESSION_ENGINE,
            'expected': 'django.contrib.sessions.backends.db',
        },
        'Session Cookie Age': {
            'setting': settings.SESSION_COOKIE_AGE,
            'expected': 1209600,  # 2 weeks
        },
        'Session Cookie HttpOnly': {
            'setting': settings.SESSION_COOKIE_HTTPONLY,
            'expected': True,
        },
        'Session Cookie SameSite': {
            'setting': settings.SESSION_COOKIE_SAMESITE,
            'expected': 'Lax',
        },
        'Email Backend': {
            'setting': settings.EMAIL_BACKEND,
            'expected': ['django.core.mail.backends.smtp.EmailBackend', 'django.core.mail.backends.console.EmailBackend'],
        },
    }
    
    all_correct = True
    for name, config in settings_to_check.items():
        setting_value = config['setting']
        expected = config['expected']
        
        if isinstance(expected, list):
            matches = setting_value in expected
            status = matches
            details = f"{setting_value} (accepted values: {', '.join(expected)})"
        else:
            matches = setting_value == expected
            status = matches
            details = f"{setting_value} (expected: {expected})"
        
        print_check(name, status, details)
        if not status:
            all_correct = False
    
    return all_correct


def verify_database():
    """Verify database tables exist."""
    print_header("DATABASE VERIFICATION")
    
    from django.contrib.sessions.models import Session
    from accounts.models import ProviderProfile, UserProfile
    
    tables_to_check = {
        'Sessions': Session,
        'ProviderProfile': ProviderProfile,
        'UserProfile': UserProfile,
    }
    
    all_exist = True
    for name, model in tables_to_check.items():
        try:
            count = model.objects.count()
            print_check(f"{name} ({count} records)", True)
        except Exception as e:
            print_check(name, False, str(e))
            all_exist = False
    
    return all_exist


def verify_email_config():
    """Verify email configuration."""
    print_header("EMAIL CONFIGURATION VERIFICATION")
    
    email_checks = {
        'EMAIL_BACKEND configured': settings.EMAIL_BACKEND != '',
        'EMAIL_HOST configured': settings.EMAIL_HOST != '',
        'EMAIL_PORT configured': settings.EMAIL_PORT > 0,
        'DEFAULT_FROM_EMAIL configured': settings.DEFAULT_FROM_EMAIL != '',
    }
    
    all_configured = True
    for check_name, result in email_checks.items():
        if check_name == 'EMAIL_BACKEND configured':
            details = settings.EMAIL_BACKEND
        elif check_name == 'EMAIL_HOST configured':
            details = f"{settings.EMAIL_HOST}:{settings.EMAIL_PORT}"
        elif check_name == 'EMAIL_PORT configured':
            details = str(settings.EMAIL_PORT)
        else:
            details = settings.DEFAULT_FROM_EMAIL
        
        print_check(check_name, result, details if result else "")
        if not result:
            all_configured = False
    
    return all_configured


def verify_urls():
    """Verify URL routes are registered."""
    print_header("URL ROUTES VERIFICATION")
    
    from django.urls import reverse
    
    routes_to_check = {
        'Provider Dashboard': 'provider_dashboard',
        'Edit Provider Profile': 'edit_provider_profile',
        'Provider Profile Detail': 'provider_profile_detail',
        'Provider Profile': 'provider_profile',
        'Home': 'home',
    }
    
    all_work = True
    for name, route_name in routes_to_check.items():
        try:
            if route_name == 'edit_provider_profile':
                url = reverse(route_name, kwargs={'provider_id': 1})
            elif route_name == 'provider_profile_detail':
                url = reverse(route_name, kwargs={'provider_id': 1})
            else:
                url = reverse(route_name)
            print_check(name, True, url)
        except Exception as e:
            print_check(name, False, str(e))
            all_work = False
    
    return all_work


def verify_templates():
    """Verify templates can be loaded."""
    print_header("TEMPLATE VERIFICATION")
    
    from django.template.loader import get_template
    from django.template.exceptions import TemplateDoesNotExist
    
    templates_to_check = {
        'Provider Dashboard': 'requests/provider_dashboard.html',
        'Provider Profile Detail': 'accounts/provider_profile_detail.html',
        'Provider Profile Edit': 'accounts/provider_profile_edit.html',
        'Profile Update Email': 'emails/profile_update_email.html',
    }
    
    all_load = True
    for name, template_name in templates_to_check.items():
        try:
            get_template(template_name)
            print_check(name, True, template_name)
        except TemplateDoesNotExist:
            print_check(name, False, f"Not found: {template_name}")
            all_load = False
        except Exception as e:
            print_check(name, False, str(e))
            all_load = False
    
    return all_load


def run_system_checks():
    """Run Django system checks."""
    print_header("DJANGO SYSTEM CHECKS")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        call_command('check')
        
        sys.stdout = old_stdout
        print_check("Django system check", True, "All checks passed")
        return True
    except Exception as e:
        sys.stdout = old_stdout
        print_check("Django system check", False, str(e))
        return False


def main():
    """Run all verifications."""
    print(f"\n{BOLD}Authentication, Session Management & RBAC Implementation Verification{RESET}\n")
    
    results = {}
    
    # Run all verifications
    results['Files'] = verify_files()
    results['Imports'] = verify_imports()
    results['Settings'] = verify_settings()
    results['Database'] = verify_database()
    results['Email Config'] = verify_email_config()
    results['URLs'] = verify_urls()
    results['Templates'] = verify_templates()
    results['System Checks'] = run_system_checks()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total Checks: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    
    print("\nDetailed Results:")
    for check_name, result in results.items():
        status_text = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {check_name}: {status_text}")
    
    # Final result
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    if failed == 0:
        print(f"{GREEN}{BOLD}✓ ALL VERIFICATIONS PASSED{RESET}")
        print(f"\nImplementation is complete and ready for testing!")
    else:
        print(f"{RED}{BOLD}✗ {failed} VERIFICATION(S) FAILED{RESET}")
        print(f"\nPlease review the failed checks above.")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
