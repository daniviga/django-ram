# Generated by Django 4.0.3 on 2022-04-09 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_rename_footer_short_siteconfiguration_footer_extended_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='homepage_content',
        ),
    ]