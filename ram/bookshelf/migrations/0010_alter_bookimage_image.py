# Generated by Django 4.2.6 on 2023-11-04 22:53

import bookshelf.models
from django.db import migrations, models
import ram.utils


class Migration(migrations.Migration):
    dependencies = [
        ("bookshelf", "0009_alter_bookimage_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookimage",
            name="image",
            field=models.ImageField(
                storage=ram.utils.DeduplicatedStorage,
                upload_to=bookshelf.models.book_image_upload,
            ),
        ),
    ]
