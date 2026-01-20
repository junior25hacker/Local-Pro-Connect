"""
Management command to calculate and update distances for existing service requests.
This should be run once after implementing the Haversine distance feature.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from requests.models import ServiceRequest
from accounts.models import ProviderProfile
from requests.distance_utils import calculate_request_distance


class Command(BaseCommand):
    help = 'Calculate and update distances for existing service requests using Haversine formula'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of requests to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without actually updating the database'
        )
        parser.add_argument(
            '--provider-id',
            type=int,
            help='Only calculate distances for requests to a specific provider'
        )
        parser.add_argument(
            '--status',
            choices=['pending', 'accepted', 'declined', 'completed'],
            help='Only process requests with specific status'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        provider_id = options.get('provider_id')
        status = options.get('status')

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting distance calculation {'(DRY RUN)' if dry_run else ''}"
            )
        )

        # Build queryset filters
        filters = {}
        if provider_id:
            filters['provider_id'] = provider_id
        if status:
            filters['status'] = status

        # Get all service requests that need distance calculation
        queryset = ServiceRequest.objects.filter(**filters).select_related(
            'provider', 'provider__provider_profile'
        )

        # Filter to only requests with coordinates and providers with coordinates
        requests_to_process = []
        for request in queryset:
            if (request.latitude and request.longitude and 
                request.provider and 
                hasattr(request.provider, 'provider_profile') and
                request.provider.provider_profile.latitude and 
                request.provider.provider_profile.longitude):
                requests_to_process.append(request)

        total_requests = len(requests_to_process)
        
        if total_requests == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No service requests found with valid coordinates for both user and provider."
                )
            )
            return

        self.stdout.write(f"Found {total_requests} requests to process")

        # Process in batches
        processed = 0
        updated = 0
        errors = 0

        for i in range(0, total_requests, batch_size):
            batch = requests_to_process[i:i + batch_size]
            batch_updated = 0

            with transaction.atomic():
                for service_request in batch:
                    try:
                        provider_profile = service_request.provider.provider_profile
                        
                        # Calculate distance
                        distance = calculate_request_distance(service_request, provider_profile)
                        
                        if distance is not None:
                            old_distance = service_request.distance_km
                            
                            if not dry_run:
                                service_request.distance_km = distance
                                service_request.save(update_fields=['distance_km'])
                            
                            batch_updated += 1
                            
                            # Log the change
                            if old_distance != distance:
                                self.stdout.write(
                                    f"Request #{service_request.id}: "
                                    f"Updated distance from {old_distance} to {distance}km"
                                )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Request #{service_request.id}: Could not calculate distance"
                                )
                            )

                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error processing request #{service_request.id}: {str(e)}"
                            )
                        )

                if dry_run:
                    # Rollback transaction in dry run mode
                    transaction.set_rollback(True)

            processed += len(batch)
            updated += batch_updated

            # Progress update
            if processed % (batch_size * 5) == 0 or processed == total_requests:
                self.stdout.write(
                    f"Processed {processed}/{total_requests} requests "
                    f"({updated} updated, {errors} errors)"
                )

        # Final summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Distance calculation completed {'(DRY RUN)' if dry_run else ''}"
            )
        )
        self.stdout.write(f"Total requests processed: {processed}")
        self.stdout.write(f"Requests updated: {updated}")
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errors encountered: {errors}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nThis was a dry run. No changes were saved to the database."
                )
            )
            self.stdout.write("Run without --dry-run to apply changes.")