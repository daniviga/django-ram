# Generated by Django 4.1.2 on 2022-10-31 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0007_rename_track_scale_tracks"),
        ("roster", "0013_rollingstock_decoder_interface"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="decoder",
            name="interface",
        ),
    ]
