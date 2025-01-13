# Generated by Django 4.2.6 on 2023-10-31 09:41

import os
import sys
import shutil
import ram.utils

from django.conf import settings
from django.db import migrations, models


def move_images(apps, schema_editor):
    sys.stdout.write("\n  Processing files. Please await...")
    model = apps.get_model("consist", "Consist")
    for r in model.objects.all():
        if not r.image:  # exit the loop if there's no image
            continue
        fname = os.path.basename(r.image.path)
        new_image = os.path.join("images", "consists", fname)
        new_path = os.path.join(settings.MEDIA_ROOT, new_image)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        try:
            shutil.move(r.image.path, new_path)
        except FileNotFoundError:
            sys.stderr.write("  !! FileNotFoundError: {}\n".format(new_image))
            pass
        r.image.name = new_image
        r.save()


class Migration(migrations.Migration):
    dependencies = [
        ("consist", "0008_alter_consist_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consist",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage,
                upload_to="images/consists",
            ),
        ),
        migrations.RunPython(
            move_images,
            reverse_code=migrations.RunPython.noop
        ),
    ]
