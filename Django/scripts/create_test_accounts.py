from django.contrib.auth.models import User
from accounts.models import ProviderProfile

def run():
    # Create test user
    if not User.objects.filter(username='testuser').exists():
        User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass123')
    # Create test provider
    if not User.objects.filter(username='testprovider').exists():
        p = User.objects.create_user(username='testprovider', email='testprovider@example.com', password='providerpass123')
        ProviderProfile.objects.create(user=p, company_name='Provider Inc', service_type='plumbing')
    print('Test user and provider created.')
