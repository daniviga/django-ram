# Generated by Django 4.0.6 on 2022-07-16 15:38

import re
from django.db import migrations, models


def gen_road_number_cleaned(apps, schema_editor):
    RollingStock = apps.get_model('roster', 'RollingStock')
    for row in RollingStock.objects.all():
        try:
            row.road_number_int = int(re.findall(r"\d+", row.road_number)[0])
            row.save(update_fields=['road_number_int'])
        except IndexError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0008_rollingstock_road_number_cleaned'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rollingstock',
            options={'ordering': ['rolling_class', 'road_number_int'], 'verbose_name_plural': 'Rolling stock'},
        ),
        migrations.RemoveField(
            model_name='rollingstock',
            name='road_number_cleaned',
        ),
        migrations.AddField(
            model_name='rollingstock',
            name='road_number_int',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(
            gen_road_number_cleaned,
            reverse_code=migrations.RunPython.noop
        ),
    ]