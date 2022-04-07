# Generated by Django 4.0.3 on 2022-04-07 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0008_property_alter_manufacturer_options_and_more'),
        ('roster', '0007_alter_rollingclass_wheel_arrangement'),
    ]

    operations = [
        migrations.CreateModel(
            name='RollingClassProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=256)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.property')),
                ('rolling_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roster.rollingclass', verbose_name='Class')),
            ],
        ),
    ]
