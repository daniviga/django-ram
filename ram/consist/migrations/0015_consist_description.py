# Generated by Django 5.1.4 on 2025-01-27 21:15

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("consist", "0014_alter_consistitem_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="consist",
            name="description",
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
