"""
Test Suite for Urgent Request Logic & Distance Calculation Architecture

Tests cover:
1. Haversine formula accuracy
2. Priority score calculation
3. Distance formatting
4. Provider queue ordering
5. Location indexing efficiency
"""

import math
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import ServiceRequest
from .distance_utils import (
    haversine_distance,
    calculate_request_distance,
    format_distance_display,
    calculate_priority_score,
    get_providers_within_radius,
)
from accounts.models import ProviderProfile, UserProfile


class HaversineFormulaTests(TestCase):
    """Test Haversine distance calculation accuracy"""
    
    def test_same_location_distance_zero(self):
        """Distance between same coordinates should be 0"""
        distance = haversine_distance(0, 0, 0, 0)
        self.assertEqual(distance, 0.0)
    
    def test_known_distance_nyc_to_la(self):
        """Test known distance: NYC (40.7128, -74.0060) to LA (34.0522, -118.2437)"""
        # Approximate great-circle distance with Earth mean radius is ~3936 km
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        self.assertGreater(distance, 3930)
        self.assertLess(distance, 3950)
    
    def test_known_distance_london_to_paris(self):
        """Test known distance: London to Paris (~340 km)"""
        distance = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertGreater(distance, 335)
        self.assertLess(distance, 345)
    
    def test_rounding_to_one_decimal(self):
        """All distances should be rounded to 1 decimal place"""
        distance = haversine_distance(40.7128, -74.0060, 40.7138, -74.0070)
        # Check that distance has at most 1 decimal place
        self.assertEqual(distance, round(distance, 1))
    
    def test_invalid_latitude_raises_error(self):
        """Latitude > 90 or < -90 should raise ValueError"""
        with self.assertRaises(ValueError):
            haversine_distance(91, 0, 0, 0)
        
        with self.assertRaises(ValueError):
            haversine_distance(-91, 0, 0, 0)
    
    def test_invalid_longitude_raises_error(self):
        """Longitude > 180 or < -180 should raise ValueError"""
        with self.assertRaises(ValueError):
            haversine_distance(0, 181, 0, 0)
        
        with self.assertRaises(ValueError):
            haversine_distance(0, -181, 0, 0)
    
    def test_antipodal_points(self):
        """Distance between antipodal points should be ~20,000 km (half Earth circumference)"""
        distance = haversine_distance(0, 0, 0, 180)
        # Half Earth's circumference: ~20,015 km
        self.assertGreater(distance, 20000)
        self.assertLess(distance, 20030)


class DistanceCalculationTests(TestCase):
    """Test distance calculation between requests and providers"""
    
    def setUp(self):
        """Create test users and profiles"""
        # Create user with request
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        # Create provider
        self.provider_user = User.objects.create_user(
            username='testprovider',
            email='provider@test.com',
            password='testpass123'
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            company_name='Test Plumbing',
            service_type='plumbing',
            latitude=Decimal('3.8667'),
            longitude=Decimal('11.5167')
        )
    
    def test_calculate_request_distance_with_valid_coordinates(self):
        """Test distance calculation with valid coordinates"""
        service_request = ServiceRequest.objects.create(
            user=self.user,
            description='Test request',
            provider_name='Test Provider',
            latitude=Decimal('3.8700'),
            longitude=Decimal('11.5200'),
            address_string='123 Test St'
        )
        
        distance = calculate_request_distance(service_request, self.provider_profile)
        self.assertIsNotNone(distance)
        self.assertGreater(distance, 0)
        self.assertLess(distance, 1)  # Should be very close
    
    def test_calculate_request_distance_without_request_coordinates(self):
        """Should return None if request has no coordinates"""
        service_request = ServiceRequest.objects.create(
            user=self.user,
            description='Test request',
            provider_name='Test Provider'
        )
        
        distance = calculate_request_distance(service_request, self.provider_profile)
        self.assertIsNone(distance)
    
    def test_calculate_request_distance_without_provider_coordinates(self):
        """Should return None if provider has no coordinates"""
        provider = ProviderProfile.objects.create(
            user=User.objects.create_user(username='noloc', password='test'),
            company_name='No Location',
            service_type='plumbing'
        )
        
        service_request = ServiceRequest.objects.create(
            user=self.user,
            description='Test request',
            provider_name='Test Provider',
            latitude=Decimal('3.8700'),
            longitude=Decimal('11.5200'),
            address_string='123 Test St'
        )
        
        distance = calculate_request_distance(service_request, provider)
        self.assertIsNone(distance)


class DistanceDisplayFormattingTests(TestCase):
    """Test distance formatting for UI display"""
    
    def test_format_distance_under_one_km(self):
        """Distances under 1 km should display in meters"""
        result = format_distance_display(0.5)
        self.assertEqual(result, "500m away")
        
        result = format_distance_display(0.1)
        self.assertEqual(result, "100m away")
    
    def test_format_distance_over_one_km(self):
        """Distances over 1 km should display in km"""
        result = format_distance_display(2.5)
        self.assertEqual(result, "2.5 km away")
        
        result = format_distance_display(15.8)
        self.assertEqual(result, "15.8 km away")
    
    def test_format_distance_none(self):
        """None distance should show 'Distance not available'"""
        result = format_distance_display(None)
        self.assertEqual(result, "Distance not available")
    
    def test_format_distance_exactly_one_km(self):
        """Exactly 1 km should display as km, not meters"""
        result = format_distance_display(1.0)
        self.assertEqual(result, "1.0 km away")


class PriorityScoreCalculationTests(TestCase):
    """Test priority score calculation for provider queues"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
    
    def test_urgent_request_bonus(self):
        """Urgent requests should get +100 points"""
        urgent_request = ServiceRequest.objects.create(
            user=self.user,
            description='Urgent test',
            provider_name='Test',
            urgent=True,
            created_at=timezone.now()
        )
        
        regular_request = ServiceRequest.objects.create(
            user=self.user,
            description='Regular test',
            provider_name='Test',
            urgent=False,
            created_at=timezone.now()
        )
        
        urgent_score = calculate_priority_score(urgent_request)
        regular_score = calculate_priority_score(regular_request)
        
        # Urgent should have approximately 100 more points
        self.assertGreaterEqual(urgent_score - regular_score, 100)
    
    def test_distance_bonus_calculation(self):
        """Closer requests should have higher priority"""
        close_request = ServiceRequest.objects.create(
            user=self.user,
            description='Close',
            provider_name='Test',
            created_at=timezone.now()
        )
        close_request.distance_km = 0.5
        
        far_request = ServiceRequest.objects.create(
            user=self.user,
            description='Far',
            provider_name='Test',
            created_at=timezone.now()
        )
        far_request.distance_km = 40.0
        
        close_score = calculate_priority_score(close_request)
        far_score = calculate_priority_score(far_request)
        
        self.assertGreater(close_score, far_score)
    
    def test_time_bonus_calculation(self):
        """Older requests should have higher priority"""
        old_request = ServiceRequest.objects.create(
            user=self.user,
            description='Old',
            provider_name='Test',
            created_at=timezone.now() - timedelta(hours=5)
        )
        
        new_request = ServiceRequest.objects.create(
            user=self.user,
            description='New',
            provider_name='Test',
            created_at=timezone.now() - timedelta(minutes=5)
        )
        
        old_score = calculate_priority_score(old_request)
        new_score = calculate_priority_score(new_request)
        
        self.assertGreater(old_score, new_score)
    
    def test_maximum_priority_score(self):
        """Maximum achievable score should be ~180"""
        max_request = ServiceRequest.objects.create(
            user=self.user,
            description='Max priority',
            provider_name='Test',
            urgent=True,
            created_at=timezone.now() - timedelta(hours=20)
        )
        max_request.distance_km = 0.0
        
        score = calculate_priority_score(max_request)
        # Score should be 100 (urgent) + 50 (distance) + 30 (time) = 180
        self.assertGreaterEqual(score, 175)
        self.assertLessEqual(score, 180)


class ProviderQueueOrderingTests(TestCase):
    """Test that requests are properly ordered in provider queues"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.provider_user = User.objects.create_user(
            username='provider',
            email='provider@test.com',
            password='testpass123'
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            company_name='Test Service',
            service_type='plumbing',
            latitude=Decimal('0.0'),
            longitude=Decimal('0.0')
        )
    
    def test_urgent_appears_before_regular(self):
        """Urgent requests should appear before regular ones"""
        # Create regular request
        regular = ServiceRequest.objects.create(
            user=self.user,
            description='Regular',
            provider_name='Test',
            urgent=False,
            created_at=timezone.now(),
            latitude=Decimal('0.0'),
            longitude=Decimal('0.0'),
            address_string='123 Test St'
        )
        regular.distance_km = 0.0
        
        # Create urgent request
        urgent = ServiceRequest.objects.create(
            user=self.user,
            description='Urgent',
            provider_name='Test',
            urgent=True,
            created_at=timezone.now(),
            latitude=Decimal('0.0'),
            longitude=Decimal('0.0'),
            address_string='123 Test St'
        )
        urgent.distance_km = 0.0
        
        regular_score = calculate_priority_score(regular)
        urgent_score = calculate_priority_score(urgent)
        
        self.assertGreater(urgent_score, regular_score)
    
    def test_closer_request_higher_priority(self):
        """Closer requests should rank higher"""
        close = ServiceRequest.objects.create(
            user=self.user,
            description='Close',
            provider_name='Test',
            urgent=False,
            created_at=timezone.now(),
            latitude=Decimal('0.0'),
            longitude=Decimal('0.0'),
            address_string='123 Test St'
        )
        close.distance_km = 1.0
        
        far = ServiceRequest.objects.create(
            user=self.user,
            description='Far',
            provider_name='Test',
            urgent=False,
            created_at=timezone.now(),
            latitude=Decimal('0.0'),
            longitude=Decimal('0.0'),
            address_string='123 Test St'
        )
        far.distance_km = 40.0
        
        close_score = calculate_priority_score(close)
        far_score = calculate_priority_score(far)
        
        self.assertGreater(close_score, far_score)


class LocationValidationTests(TestCase):
    """Test location validation in requests"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
    
    def test_request_with_valid_coordinates(self):
        """Request with valid coordinates should pass validation"""
        request = ServiceRequest(
            user=self.user,
            description='Test',
            provider_name='Test',
            latitude=Decimal('3.8667'),
            longitude=Decimal('11.5167'),
            address_string='123 Test St'
        )
        
        # Should not raise error
        request.clean()
        request.save()
        self.assertTrue(request.id)
    
    def test_request_invalid_latitude(self):
        """Request with latitude > 90 should fail validation"""
        from django.core.exceptions import ValidationError
        
        request = ServiceRequest(
            user=self.user,
            description='Test',
            provider_name='Test',
            latitude=Decimal('91'),
            longitude=Decimal('0'),
            address_string='123 Test St'
        )
        
        with self.assertRaises(ValidationError):
            request.clean()
    
    def test_has_location_method(self):
        """has_location() should return correct status"""
        # Request with location
        with_location = ServiceRequest.objects.create(
            user=self.user,
            description='Test',
            provider_name='Test',
            latitude=Decimal('3.8667'),
            longitude=Decimal('11.5167'),
            address_string='123 Test St'
        )
        
        self.assertTrue(with_location.has_location())
        
        # Request without location
        without_location = ServiceRequest.objects.create(
            user=self.user,
            description='Test 2',
            provider_name='Test 2'
        )
        
        self.assertFalse(without_location.has_location())


class APIEndpointTests(TestCase):
    """Test priority queue API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        # Create provider
        self.provider_user = User.objects.create_user(
            username='provider',
            email='provider@test.com',
            password='testpass123'
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            company_name='Test Service',
            service_type='plumbing',
            latitude=Decimal('3.8667'),
            longitude=Decimal('11.5167')
        )
    
    def test_provider_pending_requests_requires_authentication(self):
        """API should require authentication"""
        response = self.client.get('/api/requests/provider/pending/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_provider_pending_requests_requires_provider_role(self):
        """Only providers can access this endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/requests/provider/pending/')
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_providers_within_radius_valid_coordinates(self):
        """API should return providers within specified radius"""
        response = self.client.get('/api/requests/providers-nearby/', {
            'latitude': '3.8667',
            'longitude': '11.5167',
            'max_distance_km': '50'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_providers_within_radius_invalid_coordinates(self):
        """API should reject invalid coordinates"""
        response = self.client.get('/api/requests/providers-nearby/', {
            'latitude': '91',  # Invalid latitude
            'longitude': '11.5167'
        })
        self.assertNotEqual(response.status_code, 200)


if __name__ == '__main__':
    import unittest
    unittest.main()
