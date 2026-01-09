import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

from django.contrib.auth.models import User

users = [
    {'username': 'perez', 'email': 'Perez@localpro.dev', 'password': 'LocalPro2025!'},
    {'username': 'hueala', 'email': 'Hueala@localpro.dev', 'password': 'LocalPro2025!'},
    {'username': 'oliver', 'email': 'Oliver@localpro.dev', 'password': 'LocalPro2025!'},
    {'username': 'michelle', 'email': 'Michelle@localpro.dev', 'password': 'LocalPro2025!'},
    {'username': 'melaine', 'email': 'Melaine@localpro.dev', 'password': 'LocalPro2025!'},
    {'username': 'sandra', 'email': 'Sandra@localpro.dev', 'password': 'LocalPro2025!'},
]

for user_data in users:
    if not User.objects.filter(username=user_data['username']).exists():
        User.objects.create_superuser(**user_data)
        print(f"Created superuser: {user_data['username']}")
    else:
        print(f"Superuser {user_data['username']} already exists")