#!/usr/bin/env python
"""
Test script to verify login API is working
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
import json

# Create a test client
client = Client()

# Check if any users exist
users = User.objects.all()
print(f"Total users in database: {users.count()}")

if users.count() > 0:
    print("\nExisting users:")
    for user in users[:5]:  # Show first 5 users
        print(f"  - Username: {user.username}, Email: {user.email}")
else:
    print("\nNo users found in database. Creating a test user...")
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"Created test user: {test_user.username}")

# Test login API
print("\n" + "="*60)
print("Testing Login API")
print("="*60)

# Try to login with first user or test user
if users.count() > 0:
    test_username = users.first().username
    print(f"\nAttempting login with username: {test_username}")
    print("Note: You need to know the password for this user")
else:
    test_username = 'testuser'
    test_password = 'testpass123'
    
    print(f"\nTest credentials:")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}")
    
    response = client.post('/accounts/auth/', {
        'action': 'signin',
        'username': test_username,
        'password': test_password,
    })
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Content: {response.content.decode()}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print("\n✅ Login successful!")
        print(f"Success message: {data.get('success')}")
        print(f"Username: {data.get('username')}")
    else:
        print("\n❌ Login failed")
