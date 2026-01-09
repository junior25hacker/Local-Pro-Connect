import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import ProviderProfile

class Command(BaseCommand):
    help = 'Seed database with 20 Cameroon professionals across all services and regions'

    # Cameroon regions
    REGIONS = [
        'Adamawa', 'Centre', 'East', 'Far North', 'Littoral',
        'North', 'Northwest', 'South', 'Southwest', 'West'
    ]

    # Major cities per region
    CITIES = {
        'Adamawa': ['Ngaoundéré', 'Meiganga', 'Tibati'],
        'Centre': ['Yaoundé', 'Mbalmayo', 'Obala', 'Eséka'],
        'East': ['Bertoua', 'Batouri', 'Abong-Mbang'],
        'Far North': ['Maroua', 'Kousseri', 'Mokolo'],
        'Littoral': ['Douala', 'Edéa', 'Nkongsamba'],
        'North': ['Garoua', 'Guider', 'Lagdo'],
        'Northwest': ['Bamenda', 'Kumbo', 'Wum'],
        'South': ['Ebolowa', 'Kribi', 'Sangmélima'],
        'Southwest': ['Buea', 'Limbe', 'Kumba', 'Tiko'],
        'West': ['Bafoussam', 'Dschang', 'Foumban']
    }

    # Cameroon first names (mix of Francophone and Anglophone)
    FIRST_NAMES = [
        'Jean', 'Marie', 'Paul', 'André', 'François', 'Pierre',
        'Emmanuel', 'Claude', 'Jacques', 'Michel',
        'Mary', 'John', 'Peter', 'Grace', 'David', 'Sarah',
        'James', 'Ruth', 'Samuel', 'Esther',
        'Ahmadou', 'Fatima', 'Ibrahim', 'Aisha',
        'Ngala', 'Njoya', 'Manga', 'Fouda', 'Kamga', 'Nkengue'
    ]

    # Cameroon last names
    LAST_NAMES = [
        'Nguyen', 'Mballa', 'Nkolo', 'Fouda', 'Manga', 'Kamga',
        'Atangana', 'Owona', 'Effa', 'Bella',
        'Tabe', 'Fon', 'Neba', 'Ngwa', 'Njie',
        'Bello', 'Hamadou', 'Issa', 'Amadou',
        'Tchoua', 'Njoya', 'Fotso', 'Wandji', 'Kuete', 'Nganou'
    ]

    # Service types from the model
    SERVICES = [
        'plumbing', 'electrical', 'carpentry', 'cleaning', 'tutoring',
        'hvac', 'roofing', 'landscaping', 'painting', 'other'
    ]

    # Company name templates
    COMPANY_TEMPLATES = {
        'plumbing': ['{name} Plumbing Services', '{name} Water Solutions', 'Reliable {name} Plumbing'],
        'electrical': ['{name} Electrical Works', '{name} Power Solutions', '{name} Electric Services'],
        'carpentry': ['{name} Woodworks', '{name} Carpentry & Furniture', 'Master {name} Carpentry'],
        'cleaning': ['{name} Cleaning Services', 'Sparkle {name} Cleaners', '{name} Professional Cleaning'],
        'tutoring': ['{name} Tutorial Center', '{name} Academic Excellence', '{name} Learning Hub'],
        'hvac': ['{name} Climate Control', '{name} HVAC Solutions', 'Cool {name} AC Services'],
        'roofing': ['{name} Roofing Experts', '{name} Roof Masters', 'Quality {name} Roofing'],
        'landscaping': ['{name} Gardens & Landscapes', '{name} Green Solutions', '{name} Landscape Design'],
        'painting': ['{name} Painting Services', 'Perfect {name} Painters', '{name} Color Masters'],
        'other': ['{name} General Services', '{name} Professional Services', '{name} Multi-Services']
    }

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed Cameroon professionals...')

        # Ensure at least one professional per service and region
        service_region_coverage = {}
        for service in self.SERVICES:
            service_region_coverage[service] = set()

        professionals_created = 0

        # Create 20 professionals
        for i in range(1, 21):
            # Select service (ensure coverage)
            if professionals_created < 10:
                # First 10: ensure each service has at least one professional
                service = self.SERVICES[professionals_created % len(self.SERVICES)]
            else:
                # Rest: random distribution
                service = random.choice(self.SERVICES)

            # Select region (ensure coverage for this service)
            available_regions = [r for r in self.REGIONS if r not in service_region_coverage.get(service, set())]
            if available_regions and len(service_region_coverage.get(service, set())) < len(self.REGIONS):
                region = random.choice(available_regions)
            else:
                region = random.choice(self.REGIONS)

            # Track coverage
            if service not in service_region_coverage:
                service_region_coverage[service] = set()
            service_region_coverage[service].add(region)

            # Generate random name
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            full_name = f"{first_name} {last_name}"

            # Create username
            username = f"pro_{service[:4]}_{i}_{last_name.lower()}"

            # Select city from region
            city = random.choice(self.CITIES[region])

            # Generate company name
            company_template = random.choice(self.COMPANY_TEMPLATES[service])
            company_name = company_template.format(name=last_name)

            # Random years of experience (1-25 years)
            years_experience = random.randint(1, 25)

            # Random rating (4.0-5.0)
            rating = round(random.uniform(4.0, 5.0), 1)

            # Random reviews count (5-200)
            total_reviews = random.randint(5, 200)

            # Random services rendered (10-500)
            services_rendered = random.randint(10, 500)

            # Random verification status (70% verified)
            is_verified = random.random() < 0.7

            # Phone number (Cameroon format)
            phone = f"+237 6{random.randint(50000000, 99999999)}"

            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name
                )

                # Create provider profile
                provider = ProviderProfile.objects.create(
                    user=user,
                    company_name=company_name,
                    service_type=service,
                    phone=phone,
                    city=city,
                    state=region,
                    business_address=f"{random.randint(1, 999)} {random.choice(['Avenue', 'Street', 'Road', 'Boulevard'])}, {city}",
                    zip_code=f"{random.randint(1000, 9999)}",
                    years_experience=years_experience,
                    rating=rating,
                    total_reviews=total_reviews,
                    services_rendered=services_rendered,
                    is_verified=is_verified,
                    bio=f"Professional {service} specialist with {years_experience} years of experience serving {city} and {region} region. "
                        f"Committed to quality service and customer satisfaction.",
                    service_description=f"Offering comprehensive {service} services including installations, repairs, and maintenance. "
                                      f"Available for residential and commercial projects."
                )

                professionals_created += 1
                verified_text = "✓ Verified" if is_verified else "Not verified"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created: {full_name} | {company_name} | {service.title()} | {city}, {region} | {years_experience} yrs | {verified_text}'
                    )
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating professional {i}: {str(e)}'))

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {professionals_created} professionals!'))
        self.stdout.write('\n📊 Coverage Summary:')
        for service in self.SERVICES:
            regions_covered = len(service_region_coverage.get(service, set()))
            self.stdout.write(f'  • {service.title()}: {regions_covered} regions covered')
