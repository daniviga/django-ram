# Generated by Django 4.1.5 on 2023-01-09 11:22

from django.db import migrations, models


from ram.utils import slugify


def create_slug(apps, schema_editor):
    fields = ["Company", "Manufacturer", "RollingStockType", "Scale"]

    for m in fields:
        model = apps.get_model("metadata", m)

        for row in model.objects.all():
            if hasattr(row, "type"):
                row.slug = slugify("{} {}".format(row.type, row.category))
            elif hasattr(row, "scale"):
                row.slug = slugify(row.scale)
            else:
                row.slug = slugify(row.name)

            row.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0010_alter_manufacturer_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="slug",
            field=models.CharField(
                editable=False, max_length=64, blank=True
            ),
        ),
        migrations.AddField(
            model_name="manufacturer",
            name="slug",
            field=models.CharField(
                editable=False, max_length=128, blank=True
            ),
        ),
        migrations.AddField(
            model_name="rollingstocktype",
            name="slug",
            field=models.CharField(
                editable=False, max_length=128, blank=True
            ),
        ),
        migrations.AddField(
            model_name="scale",
            name="slug",
            field=models.CharField(
                editable=False, max_length=32, blank=True
            ),
        ),
        migrations.RunPython(
            create_slug,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="company",
            name="slug",
            field=models.CharField(
                editable=False, max_length=64, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="manufacturer",
            name="slug",
            field=models.CharField(
                editable=False, max_length=128, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="rollingstocktype",
            name="slug",
            field=models.CharField(
                editable=False, max_length=128, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="scale",
            name="slug",
            field=models.CharField(
                editable=False, max_length=32, unique=True
            ),
        ),
    ]
