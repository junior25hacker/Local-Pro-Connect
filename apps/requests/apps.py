from django.apps import AppConfig
from django.db import migrations


class RequestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.requests"

    
def create_price_ranges(apps, schema_editor):
    PriceRange = apps.get_model("requests", "PriceRange")
    price_ranges = [
        ("500 – 5,000", 500, 5000),
        ("5,000 – 10,000", 5000, 10000),
        ("10,000 – 20,000", 10000, 20000),
        ("20,000 – 40,000", 20000, 40000),
        ("40,000 – 60,000", 40000, 60000),
        ("60,000 – 80,000", 60000, 80000),
        ("80,000 – 100,000", 80000, 100000),
        ("100,000+", 100000, None),
    ]

    for label, min_p, max_p in price_ranges:
        PriceRange.objects.get_or_create(
            label=label,
            defaults={
                "min_price": min_p,
                "max_price": max_p,
            },
        )

class Migration(migrations.Migration):

    dependencies = [
        ("requests", "0001_initial"),  # replace with your actual last migration
    ]

    operations = [
        migrations.RunPython(create_price_ranges),
    ]