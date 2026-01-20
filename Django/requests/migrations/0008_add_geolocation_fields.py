# Generated migration for adding geolocation support to ServiceRequest model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0007_alter_requestphoto_options_requestphoto_file_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='address_string',
            field=models.CharField(max_length=500, blank=True, help_text="Full address string provided by user"),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='latitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS latitude coordinate"),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS longitude coordinate"),
        ),
    ]