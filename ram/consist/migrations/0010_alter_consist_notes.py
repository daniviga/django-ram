# Generated by Django 5.0.2 on 2024-02-17 12:19

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("consist", "0009_alter_consist_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consist",
            name="notes",
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
