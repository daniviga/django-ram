# Generated by Django 4.0.6 on 2022-07-15 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_alter_rollingstocktype_options_and_more'),
        ('consist', '0003_consist_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consist',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.company'),
        ),
    ]
