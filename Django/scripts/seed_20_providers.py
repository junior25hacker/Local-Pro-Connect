#!/usr/bin/env python
"""
Seeding Script: 20 Dummy Providers with Location Distribution
==============================================================

This script seeds 20 dummy providers across various locations with realistic data.
Features:
- Distributed across all 10 service types (2 per type)
- Diverse US locations with coordinates
- Realistic pricing (50-300 range)
- Varied experience levels (1-20 years)
- Mix of verified (60%) and unverified (40%) profiles

Usage:
    python manage.py shell < scripts/seed_20_providers.py
    OR
    python scripts/seed_20_providers.py
"""

import os
import sys
import django
from decimal import Decimal
from random import choice, randint, uniform

# Setup Django if running as script
if __name__ == '__main__' and 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
    django.setup()

from django.contrib.auth.models import User
from accounts.models import ProviderProfile

# Data for seeding
PROVIDER_SEED_DATA = [
    # PLUMBING (2)
    {
        'username': 'plumber_john',
        'email': 'john.plumber@example.com',
        'first_name': 'John',
        'last_name': 'Patterson',
        'company_name': "Patterson's Professional Plumbing",
        'service_type': 'plumbing',
        'phone': '(555) 123-4567',
        'business_address': '456 Water St',
        'city': 'Dallas',
        'state': 'TX',
        'zip_code': '75201',
        'latitude': Decimal('32.7767'),
        'longitude': Decimal('-96.7970'),
        'years_experience': 15,
        'min_price': Decimal('75.00'),
        'is_verified': True,
    },
    {
        'username': 'plumber_mike',
        'email': 'mike.plumber@example.com',
        'first_name': 'Mike',
        'last_name': 'Thompson',
        'company_name': "Thompson's Plumbing Solutions",
        'service_type': 'plumbing',
        'phone': '(555) 234-5678',
        'business_address': '789 Pipe Ave',
        'city': 'Austin',
        'state': 'TX',
        'zip_code': '78701',
        'latitude': Decimal('30.2672'),
        'longitude': Decimal('-97.7431'),
        'years_experience': 8,
        'min_price': Decimal('65.00'),
        'is_verified': False,
    },
    # ELECTRICAL (2)
    {
        'username': 'electrician_sarah',
        'email': 'sarah.electric@example.com',
        'first_name': 'Sarah',
        'last_name': 'Martinez',
        'company_name': "Martinez Electric Co.",
        'service_type': 'electrical',
        'phone': '(555) 345-6789',
        'business_address': '123 Circuit Ln',
        'city': 'Los Angeles',
        'state': 'CA',
        'zip_code': '90001',
        'latitude': Decimal('34.0522'),
        'longitude': Decimal('-118.2437'),
        'years_experience': 12,
        'min_price': Decimal('85.00'),
        'is_verified': True,
    },
    {
        'username': 'electrician_dave',
        'email': 'dave.electric@example.com',
        'first_name': 'Dave',
        'last_name': 'Wilson',
        'company_name': "Wilson's Electrical Services",
        'service_type': 'electrical',
        'phone': '(555) 456-7890',
        'business_address': '456 Voltage St',
        'city': 'San Francisco',
        'state': 'CA',
        'zip_code': '94102',
        'latitude': Decimal('37.7749'),
        'longitude': Decimal('-122.4194'),
        'years_experience': 18,
        'min_price': Decimal('100.00'),
        'is_verified': True,
    },
    # CARPENTRY (2)
    {
        'username': 'carpenter_james',
        'email': 'james.wood@example.com',
        'first_name': 'James',
        'last_name': 'Anderson',
        'company_name': "Anderson Custom Woodwork",
        'service_type': 'carpentry',
        'phone': '(555) 567-8901',
        'business_address': '789 Oak St',
        'city': 'Chicago',
        'state': 'IL',
        'zip_code': '60601',
        'latitude': Decimal('41.8781'),
        'longitude': Decimal('-87.6298'),
        'years_experience': 20,
        'min_price': Decimal('95.00'),
        'is_verified': True,
    },
    {
        'username': 'carpenter_kevin',
        'email': 'kevin.wood@example.com',
        'first_name': 'Kevin',
        'last_name': 'Davis',
        'company_name': "Davis Carpentry",
        'service_type': 'carpentry',
        'phone': '(555) 678-9012',
        'business_address': '321 Lumber Ave',
        'city': 'Phoenix',
        'state': 'AZ',
        'zip_code': '85001',
        'latitude': Decimal('33.4484'),
        'longitude': Decimal('-112.0742'),
        'years_experience': 5,
        'min_price': Decimal('70.00'),
        'is_verified': False,
    },
    # CLEANING (2)
    {
        'username': 'cleaner_lisa',
        'email': 'lisa.clean@example.com',
        'first_name': 'Lisa',
        'last_name': 'Garcia',
        'company_name': "Garcia's Professional Cleaning",
        'service_type': 'cleaning',
        'phone': '(555) 789-0123',
        'business_address': '654 Shine Ln',
        'city': 'Houston',
        'state': 'TX',
        'zip_code': '77001',
        'latitude': Decimal('29.7604'),
        'longitude': Decimal('-95.3698'),
        'years_experience': 9,
        'min_price': Decimal('50.00'),
        'is_verified': True,
    },
    {
        'username': 'cleaner_maria',
        'email': 'maria.clean@example.com',
        'first_name': 'Maria',
        'last_name': 'Rodriguez',
        'company_name': "Rodriguez Cleaning Services",
        'service_type': 'cleaning',
        'phone': '(555) 890-1234',
        'business_address': '987 Sparkle Dr',
        'city': 'Miami',
        'state': 'FL',
        'zip_code': '33101',
        'latitude': Decimal('25.7617'),
        'longitude': Decimal('-80.1918'),
        'years_experience': 6,
        'min_price': Decimal('55.00'),
        'is_verified': False,
    },
    # TUTORING (2)
    {
        'username': 'tutor_robert',
        'email': 'robert.tutor@example.com',
        'first_name': 'Robert',
        'last_name': 'Johnson',
        'company_name': "Johnson Academic Tutoring",
        'service_type': 'tutoring',
        'phone': '(555) 901-2345',
        'business_address': '111 School Rd',
        'city': 'Boston',
        'state': 'MA',
        'zip_code': '02101',
        'latitude': Decimal('42.3601'),
        'longitude': Decimal('-71.0589'),
        'years_experience': 14,
        'min_price': Decimal('60.00'),
        'is_verified': True,
    },
    {
        'username': 'tutor_jennifer',
        'email': 'jennifer.tutor@example.com',
        'first_name': 'Jennifer',
        'last_name': 'White',
        'company_name': "White Educational Services",
        'service_type': 'tutoring',
        'phone': '(555) 012-3456',
        'business_address': '222 Learning Ln',
        'city': 'Seattle',
        'state': 'WA',
        'zip_code': '98101',
        'latitude': Decimal('47.6062'),
        'longitude': Decimal('-122.3321'),
        'years_experience': 11,
        'min_price': Decimal('65.00'),
        'is_verified': True,
    },
    # HVAC (2)
    {
        'username': 'hvac_chris',
        'email': 'chris.hvac@example.com',
        'first_name': 'Chris',
        'last_name': 'Brown',
        'company_name': "Brown Heating & Cooling",
        'service_type': 'hvac',
        'phone': '(555) 123-4567',
        'business_address': '333 Temperature Blvd',
        'city': 'Denver',
        'state': 'CO',
        'zip_code': '80202',
        'latitude': Decimal('39.7392'),
        'longitude': Decimal('-104.9903'),
        'years_experience': 16,
        'min_price': Decimal('120.00'),
        'is_verified': True,
    },
    {
        'username': 'hvac_mark',
        'email': 'mark.hvac@example.com',
        'first_name': 'Mark',
        'last_name': 'Green',
        'company_name': "Green Climate Control",
        'service_type': 'hvac',
        'phone': '(555) 234-5678',
        'business_address': '444 Comfort Ln',
        'city': 'Atlanta',
        'state': 'GA',
        'zip_code': '30303',
        'latitude': Decimal('33.7490'),
        'longitude': Decimal('-84.3880'),
        'years_experience': 10,
        'min_price': Decimal('100.00'),
        'is_verified': False,
    },
    # ROOFING (2)
    {
        'username': 'roofer_david',
        'email': 'david.roof@example.com',
        'first_name': 'David',
        'last_name': 'Taylor',
        'company_name': "Taylor Roofing Experts",
        'service_type': 'roofing',
        'phone': '(555) 345-6789',
        'business_address': '555 Shingle St',
        'city': 'Philadelphia',
        'state': 'PA',
        'zip_code': '19101',
        'latitude': Decimal('39.9526'),
        'longitude': Decimal('-75.1652'),
        'years_experience': 19,
        'min_price': Decimal('150.00'),
        'is_verified': True,
    },
    {
        'username': 'roofer_edward',
        'email': 'edward.roof@example.com',
        'first_name': 'Edward',
        'last_name': 'Lee',
        'company_name': "Lee's Roofing Solutions",
        'service_type': 'roofing',
        'phone': '(555) 456-7890',
        'business_address': '666 Peak Ave',
        'city': 'Charlotte',
        'state': 'NC',
        'zip_code': '28202',
        'latitude': Decimal('35.2271'),
        'longitude': Decimal('-80.8431'),
        'years_experience': 7,
        'min_price': Decimal('130.00'),
        'is_verified': False,
    },
    # LANDSCAPING (2)
    {
        'username': 'landscaper_paul',
        'email': 'paul.landscape@example.com',
        'first_name': 'Paul',
        'last_name': 'Miller',
        'company_name': "Miller's Landscape Design",
        'service_type': 'landscaping',
        'phone': '(555) 567-8901',
        'business_address': '777 Garden Ln',
        'city': 'Portland',
        'state': 'OR',
        'zip_code': '97201',
        'latitude': Decimal('45.5152'),
        'longitude': Decimal('-122.6784'),
        'years_experience': 13,
        'min_price': Decimal('80.00'),
        'is_verified': True,
    },
    {
        'username': 'landscaper_thomas',
        'email': 'thomas.landscape@example.com',
        'first_name': 'Thomas',
        'last_name': 'Harris',
        'company_name': "Harris Outdoor Services",
        'service_type': 'landscaping',
        'phone': '(555) 678-9012',
        'business_address': '888 Grass Ave',
        'city': 'San Antonio',
        'state': 'TX',
        'zip_code': '78201',
        'latitude': Decimal('29.4241'),
        'longitude': Decimal('-98.4936'),
        'years_experience': 4,
        'min_price': Decimal('70.00'),
        'is_verified': False,
    },
    # PAINTING (2)
    {
        'username': 'painter_richard',
        'email': 'richard.paint@example.com',
        'first_name': 'Richard',
        'last_name': 'Clark',
        'company_name': "Clark Professional Painting",
        'service_type': 'painting',
        'phone': '(555) 789-0123',
        'business_address': '999 Brush St',
        'city': 'Detroit',
        'state': 'MI',
        'zip_code': '48201',
        'latitude': Decimal('42.3314'),
        'longitude': Decimal('-83.0458'),
        'years_experience': 11,
        'min_price': Decimal('75.00'),
        'is_verified': True,
    },
    {
        'username': 'painter_william',
        'email': 'william.paint@example.com',
        'first_name': 'William',
        'last_name': 'Lewis',
        'company_name': "Lewis & Sons Painting",
        'service_type': 'painting',
        'phone': '(555) 890-1234',
        'business_address': '101 Color Ln',
        'city': 'Memphis',
        'state': 'TN',
        'zip_code': '38103',
        'latitude': Decimal('35.1495'),
        'longitude': Decimal('-90.0490'),
        'years_experience': 8,
        'min_price': Decimal('60.00'),
        'is_verified': False,
    },
    # OTHER (2)
    {
        'username': 'misc_andrew',
        'email': 'andrew.services@example.com',
        'first_name': 'Andrew',
        'last_name': 'Walker',
        'company_name': "Walker General Services",
        'service_type': 'other',
        'phone': '(555) 901-2345',
        'business_address': '202 Utility Rd',
        'city': 'Las Vegas',
        'state': 'NV',
        'zip_code': '89101',
        'latitude': Decimal('36.1699'),
        'longitude': Decimal('-115.1398'),
        'years_experience': 6,
        'min_price': Decimal('55.00'),
        'is_verified': True,
    },
    {
        'username': 'misc_steven',
        'email': 'steven.services@example.com',
        'first_name': 'Steven',
        'last_name': 'King',
        'company_name': "King Multi-Services",
        'service_type': 'other',
        'phone': '(555) 012-3456',
        'business_address': '303 Service Way',
        'city': 'Louisville',
        'state': 'KY',
        'zip_code': '40202',
        'latitude': Decimal('38.2527'),
        'longitude': Decimal('-85.7585'),
        'years_experience': 3,
        'min_price': Decimal('50.00'),
        'is_verified': False,
    },
]


def seed_providers():
    """
    Seed 20 providers into the database.
    Returns count of created providers and any errors.
    """
    created_count = 0
    skipped_count = 0
    errors = []

    print("\n" + "="*70)
    print("SEEDING 20 PROVIDERS")
    print("="*70)

    for i, provider_data in enumerate(PROVIDER_SEED_DATA, 1):
        try:
            username = provider_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                print(f"   [{i:2d}] SKIP: {username} (already exists)")
                skipped_count += 1
                continue

            # Create User
            user = User.objects.create_user(
                username=username,
                email=provider_data['email'],
                first_name=provider_data['first_name'],
                last_name=provider_data['last_name'],
                password='temppass123'  # Temporary password
            )

            # Create ProviderProfile
            profile_data = {
                'user': user,
                'company_name': provider_data.get('company_name', ''),
                'service_type': provider_data.get('service_type', 'other'),
                'phone': provider_data.get('phone', ''),
                'business_address': provider_data.get('business_address', ''),
                'city': provider_data.get('city', ''),
                'state': provider_data.get('state', ''),
                'zip_code': provider_data.get('zip_code', ''),
                'latitude': provider_data.get('latitude'),
                'longitude': provider_data.get('longitude'),
                'years_experience': provider_data.get('years_experience', 0),
                'min_price': provider_data.get('min_price', Decimal('50.00')),
                'is_verified': provider_data.get('is_verified', False),
                'rating': Decimal('4.5') if provider_data.get('is_verified') else Decimal('3.0'),
                'total_reviews': randint(5, 50) if provider_data.get('is_verified') else 0,
            }
            
            provider = ProviderProfile.objects.create(**profile_data)
            
            service_display = dict(ProviderProfile.SERVICE_CHOICES).get(
                provider_data['service_type'], 
                'Other'
            )
            
            print(f"   [{i:2d}] ✓ {provider_data['first_name']:12} {provider_data['last_name']:15} | "
                  f"{service_display:15} | {provider_data['city']}, {provider_data['state']}")
            
            created_count += 1

        except Exception as e:
            error_msg = f"Error seeding {provider_data.get('username', 'Unknown')}: {str(e)}"
            print(f"   [{i:2d}] ✗ {error_msg}")
            errors.append(error_msg)

    print("\n" + "="*70)
    print("SEEDING COMPLETE")
    print("="*70)
    print(f"   Created:  {created_count} providers")
    print(f"   Skipped:  {skipped_count} providers (already exist)")
    print(f"   Errors:   {len(errors)} errors")
    
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"   - {error}")
    
    print("="*70 + "\n")

    return {
        'created': created_count,
        'skipped': skipped_count,
        'errors': errors
    }


if __name__ == '__main__':
    result = seed_providers()
    sys.exit(0 if len(result['errors']) == 0 else 1)
else:
    # When run via Django shell
    result = seed_providers()
