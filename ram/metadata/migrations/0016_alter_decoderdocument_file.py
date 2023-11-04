# Generated by Django 4.2.6 on 2023-11-04 22:53

from django.db import migrations, models
import ram.utils


class Migration(migrations.Migration):
    dependencies = [
        ("metadata", "0015_alter_company_logo_alter_decoder_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="decoderdocument",
            name="file",
            field=models.FileField(
                storage=ram.utils.DeduplicatedStorage(), upload_to="files/"
            ),
        ),
    ]