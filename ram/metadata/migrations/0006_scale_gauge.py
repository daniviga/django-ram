# Generated by Django 4.0.6 on 2022-07-18 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0005_rename_gauge_scale_track'),
    ]

    operations = [
        migrations.AddField(
            model_name='scale',
            name='gauge',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]
