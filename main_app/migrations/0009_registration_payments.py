# Generated by Django 5.1.4 on 2024-12-09 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_remove_registration_event_name_delete_payments_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('amount', models.IntegerField()),
                ('event_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.events')),
            ],
            options={
                'db_table': 'registration',
            },
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_request_id', models.CharField(max_length=100)),
                ('checkout_request_id', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=30, null=True)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.registration')),
            ],
            options={
                'db_table': 'payments',
            },
        ),
    ]
