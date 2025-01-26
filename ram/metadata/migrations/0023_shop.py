# Generated by Django 5.1.4 on 2025-01-26 14:27

import django_countries.fields
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0022_decoderdocument_creation_time_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Shop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, unique=True)),
                (
                    "country",
                    django_countries.fields.CountryField(blank=True, max_length=2),
                ),
                ("website", models.URLField(blank=True)),
                ("on_line", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": [django.db.models.functions.text.Lower("name")],
            },
        ),
    ]
