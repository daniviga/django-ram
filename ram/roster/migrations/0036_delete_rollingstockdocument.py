# Generated by Django 5.1.4 on 2025-02-09 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0035_alter_rollingstock_shop"),
        ("repository", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="RollingStockDocument",
        ),
    ]
