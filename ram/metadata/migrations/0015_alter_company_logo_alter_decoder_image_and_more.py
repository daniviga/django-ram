# Generated by Django 4.2.6 on 2023-10-30 13:16

import os
import sys
import shutil
import ram.utils

from django.conf import settings
from django.db import migrations, models


def move_images(apps, schema_editor):
    fields = {
        "Company": ["companies", "logo"],
        "Decoder": ["decoders", "image"],
        "Manufacturer": ["manufacturers", "logo"],
    }
    sys.stdout.write("\n  Processing files. Please await...")
    for m in fields.items():
        model = apps.get_model("metadata", m[0])
        for r in model.objects.all():
            field = getattr(r, m[1][1])
            if not field:  # exit the loop if there's no image
                continue
            fname = os.path.basename(field.path)
            new_image = os.path.join("images", m[1][0], fname)
            new_path = os.path.join(settings.MEDIA_ROOT, new_image)
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            try:
                shutil.move(field.path, new_path)
            except FileNotFoundError:
                sys.stderr.write(
                    "  !! FileNotFoundError: {}\n".format(new_image)
                )
                pass
            field.name = new_image
            r.save()


class Migration(migrations.Migration):
    dependencies = [
        ("metadata", "0014_alter_decoder_options_alter_tag_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage,
                upload_to="images/companies",
            ),
        ),
        migrations.AlterField(
            model_name="decoder",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage,
                upload_to="images/decoders",
            ),
        ),
        migrations.AlterField(
            model_name="manufacturer",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage,
                upload_to="images/manufacturers",
            ),
        ),
        migrations.RunPython(
            move_images,
            reverse_code=migrations.RunPython.noop
        ),
    ]
