# Generated by Django 4.0.3 on 2022-04-10 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0003_alter_driverconfiguration_network_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverconfiguration',
            name='remote_host',
            field=models.GenericIPAddressField(default='192.168.4.1', protocol='IPv4'),
        ),
    ]
