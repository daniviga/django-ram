# Generated by Django 4.0.3 on 2022-04-07 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0008_rollingclassproperty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rollingclass',
            name='wheel_arrangement',
        ),
    ]
