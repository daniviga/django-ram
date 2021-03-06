# Generated by Django 4.0.3 on 2022-04-07 09:25

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
                ('timeout', models.SmallIntegerField(default=250)),
            ],
            options={
                'verbose_name': 'Configuration',
            },
        ),
    ]
