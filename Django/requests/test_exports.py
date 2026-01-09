"""
Tests for service request export functionality.

Run with: python manage.py test requests.test_exports
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import csv
import io

from .models import ServiceRequest, PriceRange

User = get_user_model()


class ExportViewsTestCase(TestCase):
    """Test cases for CSV and PDF export views."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@test.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create price ranges
        self.price_range1 = PriceRange.objects.create(
            label='$20-50',
            min_price=20,
            max_price=50
        )
        self.price_range2 = PriceRange.objects.create(
            label='$50-100',
            min_price=50,
            max_price=100
        )
        
        # Create test service requests
        now = timezone.now()
        self.request1 = ServiceRequest.objects.create(
            user=self.user1,
            provider_name='John Plumber',
            description='Fix the leaky faucet',
            price_range=self.price_range1,
            urgent=False,
            status='pending',
            created_at=now - timedelta(days=5)
        )
        
        self.request2 = ServiceRequest.objects.create(
            user=self.user1,
            provider_name='Electric Pro',
            description='Install ceiling fan',
            price_range=self.price_range2,
            urgent=True,
            status='accepted',
            provider=self.user2,
            created_at=now - timedelta(days=2)
        )
        
        self.request3 = ServiceRequest.objects.create(
            user=self.user2,
            provider_name='Garden Master',
            description='Landscape the backyard',
            price_range=self.price_range1,
            urgent=False,
            status='declined',
            created_at=now - timedelta(days=1)
        )
        
        self.client = Client()
    
    def test_export_csv_requires_login(self):
        """Test that CSV export requires authentication."""
        response = self.client.get('/requests/export/csv/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_export_pdf_requires_login(self):
        """Test that PDF export requires authentication."""
        response = self.client.get('/requests/export/pdf/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_export_csv_basic(self):
        """Test basic CSV export without filters."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('service_requests_', response['Content-Disposition'])
        
        # Parse CSV and verify content
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # User1 should see 2 requests (request1 and request2)
        self.assertEqual(len(rows), 2)
    
    def test_export_csv_with_status_filter(self):
        """Test CSV export with status filter."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/?status=pending')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Should only see 1 pending request
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Status'], 'Pending')
    
    def test_export_csv_with_service_type_filter(self):
        """Test CSV export with service type filter."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/?service_type=Electric')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Should only see request with Electric Pro
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Service Type'], 'Electric Pro')
    
    def test_export_csv_with_urgent_filter(self):
        """Test CSV export with urgent filter."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/?urgent=true')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Should only see 1 urgent request
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Urgent'], 'Yes')
    
    def test_export_csv_with_date_filter(self):
        """Test CSV export with date filters."""
        self.client.login(username='testuser1', password='testpass123')
        
        # Filter requests from the last 3 days
        response = self.client.get('/requests/export/csv/?date_from=2024-11-27')
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Should see requests within date range
        self.assertGreater(len(rows), 0)
    
    def test_export_csv_no_results(self):
        """Test CSV export when no requests match filters."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/?status=declined')
        
        # User1 has no declined requests
        self.assertEqual(response.status_code, 204)  # No Content
    
    def test_export_csv_columns_present(self):
        """Test that all expected columns are present in CSV."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        expected_columns = [
            'Request ID',
            'Service Type',
            'User Name',
            'Provider Name',
            'Status',
            'Date Created',
            'Distance (miles)',
            'Price Range',
            'Urgent',
            'Description'
        ]
        
        self.assertEqual(reader.fieldnames, expected_columns)
    
    def test_export_pdf_basic(self):
        """Test basic PDF export without filters."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/pdf/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('service_requests_', response['Content-Disposition'])
    
    def test_export_pdf_with_filters(self):
        """Test PDF export with filters."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/pdf/?status=accepted&urgent=true')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_export_pdf_no_results(self):
        """Test PDF export when no requests match filters."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/pdf/?status=declined')
        
        # User1 has no declined requests
        self.assertEqual(response.status_code, 204)  # No Content
    
    def test_user_isolation(self):
        """Test that users only see their own requests."""
        # User1 should only see their 2 requests
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/')
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(len(rows), 2)
        self.client.logout()
        
        # User2 should only see their 1 request
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.get('/requests/export/csv/')
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(len(rows), 1)
    
    def test_combined_filters(self):
        """Test CSV export with multiple filters combined."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/?status=accepted&urgent=true')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Should only see request2 which is both accepted and urgent
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Status'], 'Accepted')
        self.assertEqual(rows[0]['Urgent'], 'Yes')
    
    def test_csv_filename_format(self):
        """Test that CSV filename has correct format."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/csv/')
        
        disposition = response['Content-Disposition']
        self.assertRegex(disposition, r'service_requests_\d{4}-\d{2}-\d{2}\.csv')
    
    def test_pdf_filename_format(self):
        """Test that PDF filename has correct format."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get('/requests/export/pdf/')
        
        disposition = response['Content-Disposition']
        self.assertRegex(disposition, r'service_requests_\d{4}-\d{2}-\d{2}\.pdf')


class ExportUtilsFunctionTestCase(TestCase):
    """Test cases for export utility functions."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.price_range = PriceRange.objects.create(
            label='$20-50',
            min_price=20,
            max_price=50
        )
        
        self.request = ServiceRequest.objects.create(
            user=self.user,
            provider_name='Test Provider',
            description='Test description',
            price_range=self.price_range,
            urgent=True,
            status='pending'
        )
    
    def test_format_request_for_export(self):
        """Test the format_request_for_export utility function."""
        from .export_utils import format_request_for_export
        
        formatted = format_request_for_export(self.request)
        
        self.assertEqual(formatted['request_id'], self.request.id)
        self.assertEqual(formatted['service_type'], 'Test Provider')
        self.assertEqual(formatted['status'], 'Pending')
        self.assertEqual(formatted['urgent'], 'Yes')
        self.assertEqual(formatted['price_range'], '$20-50')
    
    def test_get_filtered_requests_basic(self):
        """Test get_filtered_requests utility function."""
        from .export_utils import get_filtered_requests
        
        requests_list = get_filtered_requests(self.user, {}, is_provider=False)
        self.assertEqual(len(requests_list), 1)
    
    def test_get_filtered_requests_with_status(self):
        """Test get_filtered_requests with status filter."""
        from .export_utils import get_filtered_requests
        
        requests_list = get_filtered_requests(
            self.user,
            {'status': 'pending'},
            is_provider=False
        )
        self.assertEqual(len(requests_list), 1)
        
        requests_list = get_filtered_requests(
            self.user,
            {'status': 'accepted'},
            is_provider=False
        )
        self.assertEqual(len(requests_list), 0)
