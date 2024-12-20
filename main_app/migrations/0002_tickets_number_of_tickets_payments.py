# Generated by Django 5.1.4 on 2024-12-09 10:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='number_of_tickets',
            field=models.IntegerField(default=1),
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
                ('tickets', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.tickets')),
            ],
        ),
    ]
