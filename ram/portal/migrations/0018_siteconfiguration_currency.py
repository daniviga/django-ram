# Generated by Django 5.1.4 on 2024-12-29 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "portal",
            "0017_alter_flatpage_content_alter_siteconfiguration_about_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="currency",
            field=models.CharField(default="EUR", max_length=3),
        ),
    ]
