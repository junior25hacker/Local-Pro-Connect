from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0011_alter_servicerequest_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('completed', 'Completed')], db_index=True, default='pending', max_length=20),
        ),
    ]
