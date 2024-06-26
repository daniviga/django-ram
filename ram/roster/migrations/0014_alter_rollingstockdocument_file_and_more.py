# Generated by Django 4.1.2 on 2022-11-27 00:10

from django.db import migrations, models
import ram.utils


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0013_rollingstock_decoder_interface"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rollingstockdocument",
            name="file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage(),
                upload_to="files/",
            ),
        ),
        migrations.AlterField(
            model_name="rollingstockimage",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=ram.utils.DeduplicatedStorage,
                upload_to="images/",
            ),
        ),
    ]
