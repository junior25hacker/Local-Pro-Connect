
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import ProviderProfile, UserProfile

print('Deleting all users and profiles...')
User.objects.all().delete()
ProviderProfile.objects.all().delete()
UserProfile.objects.all().delete()
print('All users and profiles have been deleted.')
