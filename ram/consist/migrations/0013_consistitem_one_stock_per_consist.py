# Generated by Django 5.1.4 on 2025-01-08 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consist", "0012_consist_published"),
        ("roster", "0030_rollingstock_price"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="consistitem",
            constraint=models.UniqueConstraint(
                fields=("consist", "rolling_stock"), name="one_stock_per_consist"
            ),
        ),
    ]
