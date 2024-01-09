# Generated by Django 5.0.1 on 2024-01-08 01:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_listing_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won', to=settings.AUTH_USER_MODEL),
        ),
    ]
