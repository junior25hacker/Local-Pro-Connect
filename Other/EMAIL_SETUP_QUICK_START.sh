#!/bin/bash
#
# EMAIL SETUP QUICK START SCRIPT
# 
# This script helps you export EMAIL_* variables and test your email configuration
# Usage: bash EMAIL_SETUP_QUICK_START.sh
#

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           LocaPro EMAIL CONFIGURATION - QUICK START               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Display menu
show_menu() {
    echo "Choose your email provider:"
    echo ""
    echo "  1) Gmail (Recommended)"
    echo "  2) Outlook / Office 365"
    echo "  3) Console Output (Development/Testing)"
    echo "  4) Manual Configuration"
    echo "  5) Display Current Configuration"
    echo "  6) Test Email Connection"
    echo "  7) Run Full Email Workflow Test"
    echo "  8) Exit"
    echo ""
}

# Gmail Configuration
setup_gmail() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                      GMAIL CONFIGURATION                           ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Prerequisites:"
    echo "  ✓ Gmail account"
    echo "  ✓ 2-Step Verification enabled"
    echo "  ✓ App password generated"
    echo ""
    echo "How to generate Gmail App Password:"
    echo "  1. Go to myaccount.google.com"
    echo "  2. Click 'Security' (left sidebar)"
    echo "  3. Scroll to 'App passwords'"
    echo "  4. Select 'Mail' and 'Windows Computer'"
    echo "  5. Copy the 16-character password"
    echo ""
    
    read -p "Enter your Gmail address: " GMAIL_ADDRESS
    read -sp "Enter your Gmail app password: " GMAIL_PASSWORD
    echo ""
    
    export SMTP_PROVIDER=gmail
    export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    export EMAIL_HOST=smtp.gmail.com
    export EMAIL_PORT=465
    export EMAIL_USE_TLS=false
    export EMAIL_USE_SSL=true
    export EMAIL_HOST_USER="$GMAIL_ADDRESS"
    export EMAIL_HOST_PASSWORD="$GMAIL_PASSWORD"
    export DEFAULT_FROM_EMAIL="$GMAIL_ADDRESS"
    export SERVER_EMAIL="$GMAIL_ADDRESS"
    export SITE_URL=http://localhost:8000
    
    echo ""
    echo "✓ Gmail configuration exported!"
    display_config
}

# Outlook Configuration
setup_outlook() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    OUTLOOK CONFIGURATION                           ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    read -p "Enter your Outlook/Office 365 email: " OUTLOOK_ADDRESS
    read -sp "Enter your Outlook password: " OUTLOOK_PASSWORD
    echo ""
    
    export SMTP_PROVIDER=outlook
    export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    export EMAIL_HOST=smtp-mail.outlook.com
    export EMAIL_PORT=465
    export EMAIL_USE_TLS=false
    export EMAIL_USE_SSL=true
    export EMAIL_HOST_USER="$OUTLOOK_ADDRESS"
    export EMAIL_HOST_PASSWORD="$OUTLOOK_PASSWORD"
    export DEFAULT_FROM_EMAIL="$OUTLOOK_ADDRESS"
    export SERVER_EMAIL="$OUTLOOK_ADDRESS"
    export SITE_URL=http://localhost:8000
    
    echo ""
    echo "✓ Outlook configuration exported!"
    display_config
}

# Console Configuration
setup_console() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║            CONSOLE OUTPUT (DEVELOPMENT/TESTING)                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⚠ WARNING: Emails will be printed to console, not actually sent"
    echo ""
    
    export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
    export DEFAULT_FROM_EMAIL=test@locapro.local
    export SITE_URL=http://localhost:8000
    
    echo "✓ Console backend configured!"
    display_config
}

# Manual Configuration
setup_manual() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                   MANUAL CONFIGURATION                             ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    read -p "EMAIL_HOST (smtp.gmail.com): " EMAIL_HOST
    read -p "EMAIL_PORT (465): " EMAIL_PORT
    read -p "EMAIL_USE_SSL (true): " EMAIL_USE_SSL
    read -p "EMAIL_USE_TLS (false): " EMAIL_USE_TLS
    read -p "EMAIL_HOST_USER: " EMAIL_HOST_USER
    read -sp "EMAIL_HOST_PASSWORD: " EMAIL_HOST_PASSWORD
    echo ""
    
    export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    export EMAIL_HOST="${EMAIL_HOST:-smtp.gmail.com}"
    export EMAIL_PORT="${EMAIL_PORT:-465}"
    export EMAIL_USE_SSL="${EMAIL_USE_SSL:-true}"
    export EMAIL_USE_TLS="${EMAIL_USE_TLS:-false}"
    export EMAIL_HOST_USER="$EMAIL_HOST_USER"
    export EMAIL_HOST_PASSWORD="$EMAIL_HOST_PASSWORD"
    export DEFAULT_FROM_EMAIL="$EMAIL_HOST_USER"
    export SERVER_EMAIL="$EMAIL_HOST_USER"
    export SITE_URL=http://localhost:8000
    
    echo ""
    echo "✓ Manual configuration exported!"
    display_config
}

# Display Current Configuration
display_config() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                  CURRENT EMAIL CONFIGURATION                       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  SMTP_PROVIDER:        ${SMTP_PROVIDER:-Not set}"
    echo "  EMAIL_BACKEND:        ${EMAIL_BACKEND:-Not set}"
    echo "  EMAIL_HOST:           ${EMAIL_HOST:-Not set}"
    echo "  EMAIL_PORT:           ${EMAIL_PORT:-Not set}"
    echo "  EMAIL_USE_SSL:        ${EMAIL_USE_SSL:-Not set}"
    echo "  EMAIL_USE_TLS:        ${EMAIL_USE_TLS:-Not set}"
    echo "  EMAIL_HOST_USER:      ${EMAIL_HOST_USER:-Not set}"
    echo "  DEFAULT_FROM_EMAIL:   ${DEFAULT_FROM_EMAIL:-Not set}"
    echo "  SITE_URL:             ${SITE_URL:-Not set}"
    echo ""
}

# Test Email Connection
test_connection() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    TESTING EMAIL CONNECTION                        ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ -z "$EMAIL_HOST_USER" ]; then
        echo "✗ EMAIL_HOST_USER not set. Configure email first!"
        return 1
    fi
    
    cd Django 2>/dev/null || { echo "✗ Must run from project root"; return 1; }
    
    echo "Testing connection..."
    python manage.py shell <<EOF
import sys
from django.conf import settings
from django.core.mail import get_connection

try:
    connection = get_connection()
    connection.open()
    print("✓ Email connection successful!")
    print(f"  Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"  From: {settings.DEFAULT_FROM_EMAIL}")
    connection.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
EOF
    
    cd .. 2>/dev/null || true
}

# Run Full Email Workflow Test
run_workflow_test() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                  RUNNING EMAIL WORKFLOW TEST                       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ -z "$EMAIL_HOST_USER" ]; then
        echo "✗ EMAIL_HOST_USER not set. Configure email first!"
        return 1
    fi
    
    cd Django 2>/dev/null || { echo "✗ Must run from project root"; return 1; }
    
    python manage.py shell < scripts/test_email_workflow.py
    
    cd .. 2>/dev/null || true
}

# Main loop
while true; do
    echo ""
    show_menu
    read -p "Select option (1-8): " choice
    
    case $choice in
        1)
            setup_gmail
            ;;
        2)
            setup_outlook
            ;;
        3)
            setup_console
            ;;
        4)
            setup_manual
            ;;
        5)
            display_config
            ;;
        6)
            test_connection
            ;;
        7)
            run_workflow_test
            ;;
        8)
            echo "Exiting..."
            break
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      SETUP COMPLETE                               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Start Django server: cd Django && python manage.py runserver"
echo "  2. Create a service request through the web UI"
echo "  3. Check your email for notifications"
echo ""
echo "For detailed information, see: EMAIL_WORKFLOW_TESTING_GUIDE.md"
echo ""
