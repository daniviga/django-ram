# Generated by Django 4.0.6 on 2022-07-18 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0006_scale_gauge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scale',
            old_name='track',
            new_name='tracks',
        ),
    ]
