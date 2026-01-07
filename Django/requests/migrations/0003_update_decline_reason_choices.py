# Generated migration for updating DECLINE_REASON_CHOICES to include 'time'

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0002_service_request_workflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='decline_reason',
            field=models.CharField(
                blank=True,
                choices=[
                    ('price', 'Price'),
                    ('distance', 'Distance'),
                    ('time', 'Time'),
                    ('other', 'Other'),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
