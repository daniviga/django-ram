# Generated by Django 4.0.6 on 2022-07-12 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consist', '0002_alter_consist_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='consist',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]