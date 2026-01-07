import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile

SERVICES = [
    'plumbing', 'electrical', 'carpentry', 'cleaning', 'tutoring',
    'hvac', 'roofing', 'landscaping', 'painting', 'other'
]
REGIONS = [
    'Adamawa', 'Centre', 'East', 'Far North', 'Littoral',
    'North', 'Northwest', 'South', 'Southwest', 'West'
]
NAMES = [
    'Jean Claude', 'Aminatou Bello', 'Eric Mbi', 'Brenda Fomum', 'Samuel Njoya',
    'Esther Ngassa', 'Pauline Talla', 'Martin Ebongue', 'Chantal Mbarga', 'Alain Ndongo',
    'Victorine Neba', 'Fabrice Tchoua', 'Josiane Mvondo', 'Serge Ngue', 'Clarisse Fokou',
    'Roland Nkem', 'Patricia Ewane', 'Gaston Mvondo', 'Sylvie Nguim', 'Emmanuel Talla',
    'Mireille Njoya', 'Boris Neba', 'Yvette Ebongue', 'Lionel Mbarga', 'Carine Ndongo'
]

class Command(BaseCommand):
    help = 'Seed 20 random professionals for all services and regions'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        ProviderProfile.objects.all().delete()
        User.objects.filter(username__startswith='demo_pro_').delete()
        used_names = set()
        professionals = []
        # Ensure at least one professional per service
        for service in SERVICES:
            name = random.choice([n for n in NAMES if n not in used_names])
            used_names.add(name)
            region = random.choice(REGIONS)
            years = random.randint(1, 30)
            username = f'demo_pro_{service}_{region}'.replace(' ', '_').lower()
            user = User.objects.create(username=username)
            professional = ProviderProfile.objects.create(
                user=user,
                company_name=f'{name} Services',
                service_type=service,
                phone=f'+2376{random.randint(10000000,99999999)}',
                business_address=f'{region} Region',
                city=region,
                state=region,
                service_description=f'Expert in {service} with {years} years experience.',
                bio=f'{name} has been providing {service} services in {region} for {years} years.',
                years_experience=years,
                rating=round(random.uniform(3.5, 5.0), 1),
                total_reviews=random.randint(1, 100),
                is_verified=True
            )
            professionals.append(professional)
        # Add remaining professionals randomly
        for i in range(20 - len(SERVICES)):
            service = random.choice(SERVICES)
            name = random.choice([n for n in NAMES if n not in used_names])
            used_names.add(name)
            region = random.choice(REGIONS)
            years = random.randint(1, 30)
            username = f'demo_pro_{service}_{region}_{i}'.replace(' ', '_').lower()
            user = User.objects.create(username=username)
            professional = ProviderProfile.objects.create(
                user=user,
                company_name=f'{name} Services',
                service_type=service,
                phone=f'+2376{random.randint(10000000,99999999)}',
                business_address=f'{region} Region',
                city=region,
                state=region,
                service_description=f'Expert in {service} with {years} years experience.',
                bio=f'{name} has been providing {service} services in {region} for {years} years.',
                years_experience=years,
                rating=round(random.uniform(3.5, 5.0), 1),
                total_reviews=random.randint(1, 100),
                is_verified=True
            )
            professionals.append(professional)
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(professionals)} professionals.'))
