# Generated by Django 5.0.2 on 2024-03-02 14:31

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookshelf", "0012_alter_book_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="description",
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
