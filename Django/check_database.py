#!/usr/bin/env python3
"""
Simple script to check database connection and configuration
Run this to verify if PostgreSQL is properly connected
"""
import os
import sys
import django
from pathlib import Path

# Add Django project to path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')

try:
    django.setup()
    from django.db import connection
    from django.conf import settings
    
    print("=== DATABASE CONNECTION CHECK ===")
    print(f"Django settings loaded: {settings.SETTINGS_MODULE}")
    print(f"DEBUG mode: {settings.DEBUG}")
    
    # Check DATABASE_URL environment variable
    database_url = os.environ.get('DATABASE_URL', 'NOT SET')
    print(f"DATABASE_URL environment variable: {database_url}")
    
    # Check Django database configuration
    db_config = settings.DATABASES['default']
    print(f"Database engine: {db_config['ENGINE']}")
    print(f"Database name: {db_config['NAME']}")
    print(f"Database host: {db_config.get('HOST', 'localhost')}")
    print(f"Database port: {db_config.get('PORT', '5432')}")
    
    # Test actual connection
    print("\n=== TESTING DATABASE CONNECTION ===")
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"Database version: {db_version}")
        
        # Check if Django tables exist
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Django tables found: {len(tables)}")
        if 'auth_user' in tables:
            print("✅ Django auth tables exist - ready for login")
        else:
            print("❌ Django auth tables missing - run migrations")
            
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Check if it's a missing DATABASE_URL issue
    if 'DATABASE_URL' not in os.environ:
        print("\n🔧 SOLUTION: Set DATABASE_URL environment variable in Render")
        print("1. Go to Render Dashboard → Your Web Service → Environment")
        print("2. Add: DATABASE_URL = (your PostgreSQL connection string)")
    
print("\n=== END CHECK ===")