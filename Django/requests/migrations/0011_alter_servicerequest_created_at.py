from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0010_servicerequest_completed_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
