# Generated by Django 5.1.7 on 2025-03-26 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market_app', '0004_offer_created_at_offer_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='updated_at',
        ),
    ]
