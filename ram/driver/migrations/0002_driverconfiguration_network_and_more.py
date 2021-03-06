# Generated by Django 4.0.3 on 2022-04-10 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverconfiguration',
            name='network',
            field=models.GenericIPAddressField(default='192.168.4.0', protocol='IPv4'),
        ),
        migrations.AddField(
            model_name='driverconfiguration',
            name='subnet_mask',
            field=models.GenericIPAddressField(default='255.255.255.0', protocol='IPv4'),
        ),
    ]
