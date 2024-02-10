# Generated by Django 5.0.1 on 2024-01-29 22:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_store_order_store_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store_order',
            name='customer',
            field=models.ForeignKey(limit_choices_to={'is_shop': True}, on_delete=django.db.models.deletion.CASCADE, related_name='coming_orders', to='main.customer'),
        ),
    ]
