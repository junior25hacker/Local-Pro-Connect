"""
Migration: Add database indexes for provider location fields.
Improves performance of distance-based queries and provider searches.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_add_user_profile_picture'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='providerprofile',
            index=models.Index(
                fields=['latitude', 'longitude'],
                name='provider_location_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='providerprofile',
            index=models.Index(
                fields=['service_type', 'is_verified', 'latitude'],
                name='provider_search_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='providerprofile',
            index=models.Index(
                fields=['user', 'latitude', 'longitude'],
                name='provider_user_location_idx',
            ),
        ),
    ]
