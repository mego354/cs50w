# Generated by Django 5.0 on 2024-01-02 01:16

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('number', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1000000001), django.core.validators.MaxValueValidator(1599999999)])),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('real_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gomla_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('market_price', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_real_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_gomla_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_market_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='main.customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('real_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('gomla_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('market_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='main.order')),
            ],
        ),
    ]
