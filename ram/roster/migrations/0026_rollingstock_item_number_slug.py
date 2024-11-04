# Generated by Django 5.0.4 on 2024-04-23 21:10

from django.db import migrations, models
from ram.utils import slugify


def gen_item_number_slug(apps, schema_editor):
    RollingStock = apps.get_model('roster', 'RollingStock')
    for row in RollingStock.objects.all():
        if row.item_number:
            row.item_number_slug = slugify(row.item_number)
            row.save(update_fields=['item_number_slug'])


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0025_rollingstock_set_alter_rollingstock_era_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rollingstock",
            name="item_number_slug",
            field=models.CharField(blank=True, editable=False, max_length=32),
        ),
        migrations.RunPython(
            gen_item_number_slug,
            reverse_code=migrations.RunPython.noop
        ),
    ]