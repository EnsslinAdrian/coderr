# Generated by Django 5.1.7 on 2025-03-26 14:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market_app', '0013_alter_review_reviewer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='business_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='business_orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='customer_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]
