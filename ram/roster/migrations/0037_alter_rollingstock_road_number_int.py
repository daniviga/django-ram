# Generated by Django 5.1.4 on 2025-05-04 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0036_delete_rollingstockdocument"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rollingstock",
            name="road_number_int",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
