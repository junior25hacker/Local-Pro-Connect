from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import ProviderProfile
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with 20+ realistic provider profiles'

    def handle(self, *args, **options):
        # Provider data - realistic companies with diverse services
        providers_data = [
            # Plumbing Services
            {
                'username': 'aquaflow_plumbing',
                'email': 'info@aquaflow.com',
                'first_name': 'John',
                'last_name': 'Mitchell',
                'company_name': 'AquaFlow Plumbing Solutions',
                'service_type': 'plumbing',
                'min_price': Decimal('75.00'),
                'max_price': Decimal('400.00'),
                'service_rate': 'fixed',
                'phone': '(555) 123-4567',
                'city': 'New York',
                'state': 'NY',
                'years_experience': 15,
                'rating': Decimal('4.8'),
                'total_reviews': 342,
                'is_verified': True,
                'bio': 'Licensed master plumber with 15 years of experience. Specializing in residential and commercial plumbing services, emergency repairs, and installations.',
            },
            {
                'username': 'swift_pipes',
                'email': 'contact@swiftpipes.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'company_name': 'Swift Pipes & Fixtures',
                'service_type': 'plumbing',
                'min_price': Decimal('75.00'),
                'max_price': Decimal('400.00'),
                'service_rate': 'fixed',
                'phone': '(555) 234-5678',
                'city': 'Los Angeles',
                'state': 'CA',
                'years_experience': 12,
                'rating': Decimal('4.6'),
                'total_reviews': 289,
                'is_verified': True,
                'bio': 'Professional plumbing contractor serving LA area. Drain cleaning, leak detection, and water heater installation.',
            },
            {
                'username': 'metro_plumbing',
                'email': 'service@metropipe.com',
                'first_name': 'Robert',
                'last_name': 'Davis',
                'company_name': 'Metro Plumbing Services',
                'service_type': 'plumbing',
                'min_price': Decimal('75.00'),
                'max_price': Decimal('400.00'),
                'service_rate': 'fixed',
                'phone': '(555) 345-6789',
                'city': 'Chicago',
                'state': 'IL',
                'years_experience': 18,
                'rating': Decimal('4.9'),
                'total_reviews': 456,
                'is_verified': True,
                'bio': 'Expert plumber with 18 years in the industry. Available for emergency service 24/7. EPA certified.',
            },
            # Electrical Services
            {
                'username': 'brightwire_electric',
                'email': 'info@brightwiree.com',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'company_name': 'BrightWire Electrical',
                'service_type': 'electrical',
                'min_price': Decimal('100.00'),
                'max_price': Decimal('500.00'),
                'service_rate': 'hourly',
                'phone': '(555) 456-7890',
                'city': 'Houston',
                'state': 'TX',
                'years_experience': 14,
                'rating': Decimal('4.7'),
                'total_reviews': 315,
                'is_verified': True,
                'bio': 'Licensed electrician providing residential and commercial electrical services. Generator installation and repair specialist.',
            },
            {
                'username': 'voltpro_electric',
                'email': 'contact@voltpro.com',
                'first_name': 'James',
                'last_name': 'Anderson',
                'company_name': 'VoltPro Electrical Solutions',
                'service_type': 'electrical',
                'min_price': Decimal('100.00'),
                'max_price': Decimal('500.00'),
                'service_rate': 'hourly',
                'phone': '(555) 567-8901',
                'city': 'Phoenix',
                'state': 'AZ',
                'years_experience': 11,
                'rating': Decimal('4.5'),
                'total_reviews': 187,
                'is_verified': True,
                'bio': 'Certified electrician specializing in home rewiring, panel upgrades, and smart home installation.',
            },
            {
                'username': 'powerwise_electric',
                'email': 'service@powerwise.com',
                'first_name': 'David',
                'last_name': 'Martinez',
                'company_name': 'PowerWise Electric Inc',
                'service_type': 'electrical',
                'min_price': Decimal('100.00'),
                'max_price': Decimal('500.00'),
                'service_rate': 'hourly',
                'phone': '(555) 678-9012',
                'city': 'Philadelphia',
                'state': 'PA',
                'years_experience': 20,
                'rating': Decimal('4.8'),
                'total_reviews': 412,
                'is_verified': True,
                'bio': 'Master electrician with 20 years of experience. Commercial projects, residential troubleshooting, and code compliance.',
            },
            # Carpentry Services
            {
                'username': 'craftwood_carpentry',
                'email': 'info@craftwood.com',
                'first_name': 'Thomas',
                'last_name': 'Thompson',
                'company_name': 'Craftwood Carpentry',
                'service_type': 'carpentry',
                'min_price': Decimal('85.00'),
                'max_price': Decimal('450.00'),
                'service_rate': 'fixed',
                'phone': '(555) 789-0123',
                'city': 'San Antonio',
                'state': 'TX',
                'years_experience': 16,
                'rating': Decimal('4.9'),
                'total_reviews': 278,
                'is_verified': True,
                'bio': 'Master carpenter crafting custom furniture, built-ins, and renovations. 16 years of fine woodworking experience.',
            },
            {
                'username': 'precision_carpentry',
                'email': 'contact@precisioncarps.com',
                'first_name': 'Michael',
                'last_name': 'Garcia',
                'company_name': 'Precision Carpentry Works',
                'service_type': 'carpentry',
                'min_price': Decimal('85.00'),
                'max_price': Decimal('450.00'),
                'service_rate': 'fixed',
                'phone': '(555) 890-1234',
                'city': 'San Diego',
                'state': 'CA',
                'years_experience': 13,
                'rating': Decimal('4.6'),
                'total_reviews': 201,
                'is_verified': True,
                'bio': 'Professional carpenter offering deck building, door installation, and custom woodwork. Insured and licensed.',
            },
            {
                'username': 'woodcraft_solutions',
                'email': 'service@woodcraft.com',
                'first_name': 'Christopher',
                'last_name': 'Rodriguez',
                'company_name': 'WoodCraft Solutions LLC',
                'service_type': 'carpentry',
                'min_price': Decimal('85.00'),
                'max_price': Decimal('450.00'),
                'service_rate': 'fixed',
                'phone': '(555) 901-2345',
                'city': 'Dallas',
                'state': 'TX',
                'years_experience': 19,
                'rating': Decimal('4.8'),
                'total_reviews': 334,
                'is_verified': True,
                'bio': 'Expert in residential renovations, cabinetry, and flooring installation. Portfolio available upon request.',
            },
            # Cleaning Services
            {
                'username': 'sparkle_clean',
                'email': 'info@sparkle.com',
                'first_name': 'Amanda',
                'last_name': 'Brown',
                'company_name': 'Sparkle Cleaning Services',
                'service_type': 'cleaning',
                'min_price': Decimal('50.00'),
                'max_price': Decimal('200.00'),
                'service_rate': 'hourly',
                'phone': '(555) 012-3456',
                'city': 'San Jose',
                'state': 'CA',
                'years_experience': 8,
                'rating': Decimal('4.7'),
                'total_reviews': 156,
                'is_verified': True,
                'bio': 'Professional house cleaning, deep cleaning, and move-in/move-out services. Eco-friendly products used.',
            },
            {
                'username': 'pristine_homes',
                'email': 'contact@pristinehomes.com',
                'first_name': 'Jessica',
                'last_name': 'Lopez',
                'company_name': 'Pristine Homes Cleaning',
                'service_type': 'cleaning',
                'min_price': Decimal('50.00'),
                'max_price': Decimal('200.00'),
                'service_rate': 'hourly',
                'phone': '(555) 123-7890',
                'city': 'Austin',
                'state': 'TX',
                'years_experience': 7,
                'rating': Decimal('4.5'),
                'total_reviews': 98,
                'is_verified': True,
                'bio': 'Thorough house cleaning with attention to detail. Weekly, bi-weekly, and monthly service available.',
            },
            {
                'username': 'shine_bright_clean',
                'email': 'service@shinebright.com',
                'first_name': 'Emily',
                'last_name': 'Taylor',
                'company_name': 'Shine Bright Cleaning Co',
                'service_type': 'cleaning',
                'min_price': Decimal('50.00'),
                'max_price': Decimal('200.00'),
                'service_rate': 'hourly',
                'phone': '(555) 234-8901',
                'city': 'Jacksonville',
                'state': 'FL',
                'years_experience': 10,
                'rating': Decimal('4.8'),
                'total_reviews': 223,
                'is_verified': True,
                'bio': 'Professional cleaning team specializing in residential and office cleaning. Licensed and bonded.',
            },
            # HVAC Services
            {
                'username': 'climate_control',
                'email': 'info@climatecontrol.com',
                'first_name': 'Kevin',
                'last_name': 'Wilson',
                'company_name': 'Climate Control HVAC',
                'service_type': 'hvac',
                'min_price': Decimal('120.00'),
                'max_price': Decimal('600.00'),
                'service_rate': 'fixed',
                'phone': '(555) 345-8901',
                'city': 'Fort Worth',
                'state': 'TX',
                'years_experience': 17,
                'rating': Decimal('4.9'),
                'total_reviews': 267,
                'is_verified': True,
                'bio': 'HVAC technician with 17 years experience. AC repair, furnace installation, and maintenance contracts available.',
            },
            {
                'username': 'cozy_comfort_hvac',
                'email': 'contact@cozycomfort.com',
                'first_name': 'Patrick',
                'last_name': 'Moore',
                'company_name': 'Cozy Comfort HVAC Services',
                'service_type': 'hvac',
                'min_price': Decimal('120.00'),
                'max_price': Decimal('600.00'),
                'service_rate': 'fixed',
                'phone': '(555) 456-9012',
                'city': 'Columbus',
                'state': 'OH',
                'years_experience': 12,
                'rating': Decimal('4.6'),
                'total_reviews': 145,
                'is_verified': False,
                'bio': 'Heating and cooling specialist. Same-day service available for emergencies.',
            },
            {
                'username': 'perfect_temp_hvac',
                'email': 'service@perfecttemp.com',
                'first_name': 'Daniel',
                'last_name': 'Jackson',
                'company_name': 'Perfect Temp HVAC',
                'service_type': 'hvac',
                'min_price': Decimal('120.00'),
                'max_price': Decimal('600.00'),
                'service_rate': 'fixed',
                'phone': '(555) 567-9012',
                'city': 'Charlotte',
                'state': 'NC',
                'years_experience': 15,
                'rating': Decimal('4.7'),
                'total_reviews': 198,
                'is_verified': True,
                'bio': 'Licensed HVAC contractor offering full system maintenance and emergency repairs 24/7.',
            },
            # Roofing Services
            {
                'username': 'roof_experts',
                'email': 'info@roofexperts.com',
                'first_name': 'Joseph',
                'last_name': 'Harris',
                'company_name': 'Roof Experts Inc',
                'service_type': 'roofing',
                'min_price': Decimal('150.00'),
                'max_price': Decimal('1000.00'),
                'service_rate': 'fixed',
                'phone': '(555) 678-0123',
                'city': 'San Francisco',
                'state': 'CA',
                'years_experience': 22,
                'rating': Decimal('4.9'),
                'total_reviews': 389,
                'is_verified': True,
                'bio': 'Master roofer with 22 years experience. Roof repair, replacement, and inspection services. Insurance approved.',
            },
            {
                'username': 'shingle_pro',
                'email': 'contact@shinglepro.com',
                'first_name': 'William',
                'last_name': 'White',
                'company_name': 'Shingle Pro Roofing',
                'service_type': 'roofing',
                'min_price': Decimal('150.00'),
                'max_price': Decimal('1000.00'),
                'service_rate': 'fixed',
                'phone': '(555) 789-1234',
                'city': 'Indianapolis',
                'state': 'IN',
                'years_experience': 11,
                'rating': Decimal('4.5'),
                'total_reviews': 112,
                'is_verified': True,
                'bio': 'Professional roofing contractor. Residential and commercial projects. Free estimates available.',
            },
            # Landscaping Services
            {
                'username': 'green_landscape',
                'email': 'info@greenscape.com',
                'first_name': 'Brandon',
                'last_name': 'Green',
                'company_name': 'Green Landscape Design',
                'service_type': 'landscaping',
                'min_price': Decimal('60.00'),
                'max_price': Decimal('300.00'),
                'service_rate': 'fixed',
                'phone': '(555) 890-2345',
                'city': 'Austin',
                'state': 'TX',
                'years_experience': 10,
                'rating': Decimal('4.6'),
                'total_reviews': 167,
                'is_verified': True,
                'bio': 'Professional landscaper offering lawn maintenance, hardscaping, and garden design. Seasonal services available.',
            },
            {
                'username': 'landscape_masters',
                'email': 'contact@landscapemasters.com',
                'first_name': 'Eric',
                'last_name': 'Clark',
                'company_name': 'Landscape Masters LLC',
                'service_type': 'landscaping',
                'min_price': Decimal('60.00'),
                'max_price': Decimal('300.00'),
                'service_rate': 'fixed',
                'phone': '(555) 901-3456',
                'city': 'Memphis',
                'state': 'TN',
                'years_experience': 14,
                'rating': Decimal('4.7'),
                'total_reviews': 203,
                'is_verified': True,
                'bio': 'Full-service landscaping company with expertise in design, installation, and maintenance.',
            },
            # Painting Services
            {
                'username': 'color_perfect_paint',
                'email': 'info@colorperfect.com',
                'first_name': 'Justin',
                'last_name': 'Martin',
                'company_name': 'Color Perfect Painting',
                'service_type': 'painting',
                'min_price': Decimal('70.00'),
                'max_price': Decimal('350.00'),
                'service_rate': 'fixed',
                'phone': '(555) 012-4567',
                'city': 'Boston',
                'state': 'MA',
                'years_experience': 13,
                'rating': Decimal('4.8'),
                'total_reviews': 256,
                'is_verified': True,
                'bio': 'Professional painter specializing in interior and exterior painting. Free color consultation included.',
            },
            {
                'username': 'brushstroke_pro',
                'email': 'contact@brushstroke.com',
                'first_name': 'Ryan',
                'last_name': 'Taylor',
                'company_name': 'BrushStroke Professional Painting',
                'service_type': 'painting',
                'min_price': Decimal('70.00'),
                'max_price': Decimal('350.00'),
                'service_rate': 'fixed',
                'phone': '(555) 123-5678',
                'city': 'Seattle',
                'state': 'WA',
                'years_experience': 9,
                'rating': Decimal('4.5'),
                'total_reviews': 134,
                'is_verified': True,
                'bio': 'Quality painting services for residential and commercial properties. Licensed and insured.',
            },
            # Tutoring Services
            {
                'username': 'math_whiz_tutoring',
                'email': 'info@mathwhiz.com',
                'first_name': 'Catherine',
                'last_name': 'Chen',
                'company_name': 'Math Whiz Tutoring',
                'service_type': 'tutoring',
                'min_price': Decimal('40.00'),
                'max_price': Decimal('150.00'),
                'service_rate': 'hourly',
                'phone': '(555) 234-6789',
                'city': 'San Francisco',
                'state': 'CA',
                'years_experience': 8,
                'rating': Decimal('4.9'),
                'total_reviews': 178,
                'is_verified': True,
                'bio': 'Experienced math tutor. SAT/ACT prep, algebra, geometry, and calculus. Online and in-person sessions available.',
            },
            {
                'username': 'english_excellence',
                'email': 'contact@englishexcel.com',
                'first_name': 'Margaret',
                'last_name': 'Smith',
                'company_name': 'English Excellence Tutoring',
                'service_type': 'tutoring',
                'min_price': Decimal('40.00'),
                'max_price': Decimal('150.00'),
                'service_rate': 'hourly',
                'phone': '(555) 345-7890',
                'city': 'New York',
                'state': 'NY',
                'years_experience': 11,
                'rating': Decimal('4.6'),
                'total_reviews': 145,
                'is_verified': True,
                'bio': 'Professional English tutor specializing in writing, literature, and ESL. Flexible scheduling available.',
            },
            # Other Services
            {
                'username': 'handy_expert',
                'email': 'info@handyexpert.com',
                'first_name': 'George',
                'last_name': 'Patterson',
                'company_name': 'Handy Expert Services',
                'service_type': 'other',
                'min_price': Decimal('50.00'),
                'max_price': Decimal('500.00'),
                'service_rate': 'custom',
                'phone': '(555) 456-8901',
                'city': 'Denver',
                'state': 'CO',
                'years_experience': 12,
                'rating': Decimal('4.6'),
                'total_reviews': 89,
                'is_verified': False,
                'bio': 'General handyman services. Repairs, installations, and home maintenance. Call for availability.',
            },
        ]

        self.stdout.write(self.style.SUCCESS('Starting provider seeding...'))
        
        created_count = 0
        skipped_count = 0

        for provider_data in providers_data:
            # Extract user-specific fields
            user_data = {
                'username': provider_data.pop('username'),
                'email': provider_data.pop('email'),
                'first_name': provider_data.pop('first_name'),
                'last_name': provider_data.pop('last_name'),
            }

            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists, skipping..."))
                skipped_count += 1
                continue

            try:
                # Create user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                )

                # Create provider profile
                provider = ProviderProfile.objects.create(
                    user=user,
                    **provider_data
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created provider: {provider.company_name} ({provider.service_type}) in {provider.city}, {provider.state}"
                    )
                )
                created_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error creating {user_data['username']}: {str(e)}"))
                skipped_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Provider Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} providers'))
        self.stdout.write(self.style.SUCCESS(f'Skipped: {skipped_count} providers'))
        
        # Verify distribution
        total_providers = ProviderProfile.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total providers in database: {total_providers}'))
        
        # Show service type distribution
        service_dist = {}
        for provider in ProviderProfile.objects.all():
            service = provider.service_type
            service_dist[service] = service_dist.get(service, 0) + 1
        
        self.stdout.write(self.style.SUCCESS('\nService Type Distribution:'))
        for service, count in sorted(service_dist.items()):
            self.stdout.write(self.style.SUCCESS(f'  {service}: {count}'))
        
        # Show location distribution
        location_dist = {}
        for provider in ProviderProfile.objects.all():
            location = f"{provider.city}, {provider.state}"
            location_dist[location] = location_dist.get(location, 0) + 1
        
        self.stdout.write(self.style.SUCCESS('\nLocation Distribution:'))
        for location, count in sorted(location_dist.items()):
            self.stdout.write(self.style.SUCCESS(f'  {location}: {count}'))
        
        self.stdout.write(self.style.SUCCESS('='*60))
