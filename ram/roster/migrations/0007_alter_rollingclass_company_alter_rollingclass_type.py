# Generated by Django 4.0.6 on 2022-07-15 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_alter_rollingstocktype_options_and_more'),
        ('roster', '0006_alter_rollingclassproperty_rolling_class_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rollingclass',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.company'),
        ),
        migrations.AlterField(
            model_name='rollingclass',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.rollingstocktype'),
        ),
    ]
