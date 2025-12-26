import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import ProviderProfile, UserProfile
from django.core.files import File

print('Starting create_test_data')

if User.objects.filter(username='testuser').exists():
    print('testuser already exists')
else:
    u = User.objects.create_user('testuser', 'test@example.com', 'pass1234')
    print('created user', u.username)
    UserProfile.objects.create(user=u)
    prof = ProviderProfile.objects.create(user=u, company_name='TestCo', service_type='plumbing', phone='123456789', business_address='1 Test St', city='Testville', state='TS', zip_code='00000', bio='I do tests', years_experience=3)
    print('created provider record id', prof.id)
    img_path = Path('media/test_images/tiny.png')
    if img_path.exists():
        with img_path.open('rb') as f:
            prof.profile_picture.save('tiny.png', File(f))
        prof.save()
        print('saved picture', prof.profile_picture.name)
    else:
        print('image file not found', img_path)

print('users:', list(User.objects.values('username', 'email')))
print('providers:', list(ProviderProfile.objects.values('id', 'user_id', 'company_name', 'profile_picture')))
