# Generated by Django 5.1.4 on 2025-05-24 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0037_alter_rollingstock_road_number_int"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rollingstock",
            name="rolling_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rolling_stock",
                to="roster.rollingclass",
                verbose_name="Class",
            ),
        ),
    ]
