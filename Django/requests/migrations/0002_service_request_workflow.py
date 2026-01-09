# Generated migration for service request workflow

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('requests', '0001_initial'),
    ]

    operations = [
        # Add new fields to ServiceRequest
        migrations.AddField(
            model_name='servicerequest',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_requests_as_provider', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='provider_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='decline_reason',
            field=models.CharField(blank=True, choices=[('price', 'Price too low'), ('distance', 'Too far away'), ('other', 'Other reason'), ('no_reason', 'No reason provided')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='decline_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='accepted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='declined_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='servicerequest',
            options={'ordering': ['-created_at']},
        ),
        # Create RequestDecisionToken model
        migrations.CreateModel(
            name='RequestDecisionToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('used', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('service_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='decision_token', to='requests.servicerequest')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
