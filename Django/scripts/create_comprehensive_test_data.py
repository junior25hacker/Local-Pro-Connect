#!/usr/bin/env python
"""
Comprehensive test data creation script for Django application.
Creates users, providers, and service requests with various statuses.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locapro_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, ProviderProfile
from requests.models import ServiceRequest, PriceRange
from django.utils import timezone


def create_price_ranges():
    """Create PriceRange objects if they don't exist"""
    print("\n" + "="*70)
    print("CREATING PRICE RANGES")
    print("="*70)
    
    price_ranges_data = [
        {"label": "Under $50", "min_price": 0, "max_price": 50},
        {"label": "$50-$100", "min_price": 50, "max_price": 100},
        {"label": "$100-$250", "min_price": 100, "max_price": 250},
        {"label": "$250-$500", "min_price": 250, "max_price": 500},
        {"label": "$500+", "min_price": 500, "max_price": None},
    ]
    
    created_count = 0
    for data in price_ranges_data:
        pr, created = PriceRange.objects.get_or_create(
            label=data["label"],
            defaults={"min_price": data["min_price"], "max_price": data["max_price"]}
        )
        if created:
            created_count += 1
            print(f"✓ Created: {pr.label}")
        else:
            print(f"✗ Already exists: {pr.label}")
    
    print(f"\nPrice Ranges Summary: {created_count} new created")
    return created_count


def create_users():
    """Create regular users with UserProfile"""
    print("\n" + "="*70)
    print("CREATING REGULAR USERS")
    print("="*70)
    
    # Different NYC zip codes
    user_data = [
        {
            "username": "john_miller",
            "email": "john.miller@example.com",
            "first_name": "John",
            "last_name": "Miller",
            "phone": "212-555-0101",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001"
        },
        {
            "username": "sarah_johnson",
            "email": "sarah.johnson@example.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "phone": "212-555-0102",
            "address": "456 Park Ave",
            "city": "New York",
            "state": "NY",
            "zip_code": "10002"
        },
        {
            "username": "mike_chen",
            "email": "mike.chen@example.com",
            "first_name": "Mike",
            "last_name": "Chen",
            "phone": "718-555-0103",
            "address": "789 Bridge St",
            "city": "Brooklyn",
            "state": "NY",
            "zip_code": "11201"
        },
        {
            "username": "diana_garcia",
            "email": "diana.garcia@example.com",
            "first_name": "Diana",
            "last_name": "Garcia",
            "phone": "718-555-0104",
            "address": "321 Forest Ave",
            "city": "Forest Hills",
            "state": "NY",
            "zip_code": "11354"
        },
    ]
    
    created_count = 0
    users = []
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created user: {user.username} ({user.first_name} {user.last_name})")
        else:
            print(f"✗ User already exists: {user.username}")
        
        # Create or update UserProfile
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "phone": data["phone"],
                "address": data["address"],
                "city": data["city"],
                "state": data["state"],
                "zip_code": data["zip_code"],
            }
        )
        
        if profile_created:
            print(f"  → UserProfile created: {data['zip_code']}")
        
        users.append(user)
    
    print(f"\nUsers Summary: {created_count} new created, {len(users)} total users available")
    return users


def create_providers():
    """Create provider users with ProviderProfile"""
    print("\n" + "="*70)
    print("CREATING PROVIDERS")
    print("="*70)
    
    provider_data = [
        {
            "username": "plumber_joe",
            "email": "joe.plumber@example.com",
            "first_name": "Joe",
            "last_name": "Plumber",
            "company_name": "Joe's Plumbing Solutions",
            "service_type": "plumbing",
            "phone": "212-555-1001",
            "business_address": "100 Water St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "service_description": "Professional plumbing services for residential and commercial properties",
            "years_experience": 15,
            "rating": Decimal("4.8"),
            "total_reviews": 42,
        },
        {
            "username": "electrician_tom",
            "email": "tom.electrician@example.com",
            "first_name": "Tom",
            "last_name": "Electrician",
            "company_name": "Tom's Electric",
            "service_type": "electrical",
            "phone": "718-555-1002",
            "business_address": "200 Power Ave",
            "city": "Brooklyn",
            "state": "NY",
            "zip_code": "11201",
            "service_description": "Licensed electrical contractor with 20+ years experience",
            "years_experience": 20,
            "rating": Decimal("4.9"),
            "total_reviews": 58,
        },
        {
            "username": "carpenter_alex",
            "email": "alex.carpenter@example.com",
            "first_name": "Alex",
            "last_name": "Carpenter",
            "company_name": "Alex's Custom Carpentry",
            "service_type": "carpentry",
            "phone": "718-555-1003",
            "business_address": "300 Wood Ln",
            "city": "Queens",
            "state": "NY",
            "zip_code": "11354",
            "service_description": "Custom woodworking and carpentry for homes and businesses",
            "years_experience": 12,
            "rating": Decimal("4.7"),
            "total_reviews": 35,
        },
        {
            "username": "cleaner_maria",
            "email": "maria.cleaner@example.com",
            "first_name": "Maria",
            "last_name": "Cleaner",
            "company_name": "Maria's Cleaning Service",
            "service_type": "cleaning",
            "phone": "212-555-1004",
            "business_address": "400 Clean St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10002",
            "service_description": "Professional cleaning services for residential and office spaces",
            "years_experience": 8,
            "rating": Decimal("4.6"),
            "total_reviews": 28,
        },
        {
            "username": "hvac_dave",
            "email": "dave.hvac@example.com",
            "first_name": "Dave",
            "last_name": "HVAC",
            "company_name": "Dave's HVAC Solutions",
            "service_type": "hvac",
            "phone": "718-555-1005",
            "business_address": "500 Cool Ave",
            "city": "Queens",
            "state": "NY",
            "zip_code": "11201",
            "service_description": "HVAC installation, repair, and maintenance",
            "years_experience": 18,
            "rating": Decimal("4.5"),
            "total_reviews": 31,
        },
    ]
    
    created_count = 0
    providers = []
    for data in provider_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created provider user: {user.username}")
        else:
            print(f"✗ Provider user already exists: {user.username}")
        
        # Create or update ProviderProfile
        profile, profile_created = ProviderProfile.objects.get_or_create(
            user=user,
            defaults={
                "company_name": data["company_name"],
                "service_type": data["service_type"],
                "phone": data["phone"],
                "business_address": data["business_address"],
                "city": data["city"],
                "state": data["state"],
                "zip_code": data["zip_code"],
                "service_description": data["service_description"],
                "years_experience": data["years_experience"],
                "rating": data["rating"],
                "total_reviews": data["total_reviews"],
                "is_verified": True,
            }
        )
        
        if profile_created:
            print(f"  → ProviderProfile created: {data['service_type'].title()} in {data['zip_code']}")
        
        providers.append(user)
    
    print(f"\nProviders Summary: {created_count} new created, {len(providers)} total providers available")
    return providers


def create_service_requests(users, providers):
    """Create ServiceRequest objects with various statuses"""
    print("\n" + "="*70)
    print("CREATING SERVICE REQUESTS")
    print("="*70)
    
    # Get price ranges
    price_ranges = list(PriceRange.objects.all())
    
    requests_data = [
        {
            "user_idx": 0,
            "provider_idx": 0,
            "description": "Fix leaky kitchen faucet and check for other issues",
            "provider_name": "Joe's Plumbing Solutions",
            "status": "pending",
            "price_range_idx": 0,
            "urgent": False,
        },
        {
            "user_idx": 0,
            "provider_idx": 1,
            "description": "Install new light fixtures in living room",
            "provider_name": "Tom's Electric",
            "status": "accepted",
            "price_range_idx": 2,
            "urgent": False,
        },
        {
            "user_idx": 1,
            "provider_idx": 2,
            "description": "Build custom shelving unit for bedroom",
            "provider_name": "Alex's Custom Carpentry",
            "status": "declined",
            "price_range_idx": 3,
            "urgent": False,
            "decline_reason": "distance",
            "decline_message": "Too far from my service area",
        },
        {
            "user_idx": 1,
            "provider_idx": 3,
            "description": "Deep clean apartment before moving in",
            "provider_name": "Maria's Cleaning Service",
            "status": "accepted",
            "price_range_idx": 1,
            "urgent": True,
        },
        {
            "user_idx": 2,
            "provider_idx": 0,
            "description": "Replace bathroom tiles and grout",
            "provider_name": "Joe's Plumbing Solutions",
            "status": "pending",
            "price_range_idx": 2,
            "urgent": False,
        },
        {
            "user_idx": 2,
            "provider_idx": 4,
            "description": "AC maintenance and filter replacement",
            "provider_name": "Dave's HVAC Solutions",
            "status": "accepted",
            "price_range_idx": 1,
            "urgent": False,
        },
        {
            "user_idx": 3,
            "provider_idx": 1,
            "description": "Upgrade electrical panel for new appliances",
            "provider_name": "Tom's Electric",
            "status": "pending",
            "price_range_idx": 4,
            "urgent": True,
        },
        {
            "user_idx": 3,
            "provider_idx": 2,
            "description": "Repair wooden deck and stain",
            "provider_name": "Alex's Custom Carpentry",
            "status": "declined",
            "price_range_idx": 3,
            "urgent": False,
            "decline_reason": "price",
            "decline_message": "Budget is too low for this project",
        },
        {
            "user_idx": 0,
            "provider_idx": 3,
            "description": "General office cleaning weekly service",
            "provider_name": "Maria's Cleaning Service",
            "status": "pending",
            "price_range_idx": 2,
            "urgent": False,
        },
        {
            "user_idx": 1,
            "provider_idx": 4,
            "description": "Install new heating system",
            "provider_name": "Dave's HVAC Solutions",
            "status": "pending",
            "price_range_idx": 4,
            "urgent": True,
        },
    ]
    
    created_count = 0
    for req_data in requests_data:
        user = users[req_data["user_idx"]]
        provider = providers[req_data["provider_idx"]]
        
        # Check if this request already exists
        request, created = ServiceRequest.objects.get_or_create(
            user=user,
            provider_name=req_data["provider_name"],
            description=req_data["description"],
            defaults={
                "status": req_data["status"],
                "price_range": price_ranges[req_data["price_range_idx"]] if price_ranges else None,
                "urgent": req_data.get("urgent", False),
                "provider": provider if req_data["status"] in ["accepted", "declined"] else None,
                "decline_reason": req_data.get("decline_reason"),
                "decline_message": req_data.get("decline_message"),
            }
        )
        
        if created:
            created_count += 1
            status_emoji = "✓"
            
            # Set accepted_at or declined_at times
            if request.status == "accepted":
                request.accepted_at = timezone.now() - timedelta(days=1)
                request.save()
            elif request.status == "declined":
                request.declined_at = timezone.now() - timedelta(hours=2)
                request.save()
            
            print(f"{status_emoji} Created request: {request.provider_name} - Status: {request.status.upper()}")
            print(f"   User: {user.username} | Zip: {user.user_profile.zip_code}")
        else:
            print(f"✗ Request already exists: {req_data['provider_name']}")
    
    print(f"\nService Requests Summary: {created_count} new created")
    return created_count


def print_summary():
    """Print summary of all created data"""
    print("\n" + "="*70)
    print("FINAL DATA SUMMARY")
    print("="*70)
    
    users_count = User.objects.filter(user_profile__isnull=False).count()
    providers_count = User.objects.filter(provider_profile__isnull=False).count()
    requests_count = ServiceRequest.objects.count()
    price_ranges_count = PriceRange.objects.count()
    
    print(f"\n📊 Database Summary:")
    print(f"   Regular Users: {users_count}")
    print(f"   Service Providers: {providers_count}")
    print(f"   Service Requests: {requests_count}")
    print(f"   Price Ranges: {price_ranges_count}")
    
    # Request status breakdown
    print(f"\n📋 Service Requests by Status:")
    pending = ServiceRequest.objects.filter(status='pending').count()
    accepted = ServiceRequest.objects.filter(status='accepted').count()
    declined = ServiceRequest.objects.filter(status='declined').count()
    print(f"   Pending: {pending}")
    print(f"   Accepted: {accepted}")
    print(f"   Declined: {declined}")
    
    # Zip code distribution
    print(f"\n📍 Users by Zip Code:")
    profiles = UserProfile.objects.select_related('user').all()
    zip_codes = {}
    for profile in profiles:
        zip_code = profile.zip_code
        if zip_code not in zip_codes:
            zip_codes[zip_code] = []
        zip_codes[zip_code].append(profile.user.username)
    
    for zip_code in sorted(zip_codes.keys()):
        print(f"   {zip_code}: {', '.join(zip_codes[zip_code])}")
    
    # Providers by service type
    print(f"\n🔧 Providers by Service Type:")
    providers = ProviderProfile.objects.select_related('user').all()
    service_types = {}
    for provider in providers:
        stype = provider.get_service_type_display()
        if stype not in service_types:
            service_types[stype] = []
        service_types[stype].append(provider.user.username)
    
    for stype in sorted(service_types.keys()):
        print(f"   {stype}: {', '.join(service_types[stype])}")
    
    print(f"\n✅ Test data creation completed!")
    print("="*70)


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST DATA CREATION")
    print("Django Application: Local Pro Connect")
    print("="*70)
    
    try:
        # Create price ranges
        create_price_ranges()
        
        # Create users
        users = create_users()
        
        # Create providers
        providers = create_providers()
        
        # Create service requests
        create_service_requests(users, providers)
        
        # Print summary
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
