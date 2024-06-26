# Generated by Django 5.0.4 on 2024-04-20 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0016_alter_decoderdocument_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="private",
            field=models.BooleanField(
                default=False, help_text="Property will be only visible to logged users"
            ),
        ),
    ]
