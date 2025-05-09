# Generated by Django 5.1.4 on 2025-01-26 14:32

import django.db.models.deletion
from django.db import migrations, models


def shop_from_property(apps, schema_editor):
    basebook = apps.get_model("bookshelf", "BaseBook")
    shop_model = apps.get_model("metadata", "Shop")
    for row in basebook.objects.all():
        property = row.property.filter(
            property__name__icontains="shop"
        ).first()
        if property:
            shop, created = shop_model.objects.get_or_create(
                name=property.value,
                defaults={"on_line": False}
            )

            row.shop = shop
            row.save()


class Migration(migrations.Migration):

    dependencies = [
        ("bookshelf", "0021_basebookdocument_creation_time_and_more"),
        ("metadata", "0023_shop"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="basebookdocument",
            name="unique_book_file",
        ),
        migrations.AddField(
            model_name="basebook",
            name="shop",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="metadata.shop",
            ),
        ),
        migrations.RunPython(
            shop_from_property,
            reverse_code=migrations.RunPython.noop
        ),
    ]
