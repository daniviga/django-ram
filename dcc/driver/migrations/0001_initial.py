# Generated by Django 4.0 on 2021-12-31 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DriverConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_host', models.GenericIPAddressField(default='192.168.4.1', protocol='IPv4')),
                ('remote_port', models.SmallIntegerField(default=2560)),
            ],
            options={
                'verbose_name': 'Driver Configuration',
            },
        ),
    ]
