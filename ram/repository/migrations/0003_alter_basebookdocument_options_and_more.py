# Generated by Django 5.1.4 on 2025-02-09 15:16

import ram.utils
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookshelf", "0023_delete_basebookdocument"),
        ("repository", "0002_alter_decoderdocument_options_and_more"),
        ("roster", "0036_delete_rollingstockdocument"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="basebookdocument",
            options={"verbose_name_plural": "Bookshelf Documents"},
        ),
        migrations.AlterModelOptions(
            name="genericdocument",
            options={"verbose_name_plural": "Generic documents"},
        ),
        migrations.CreateModel(
            name="InvoiceDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=128)),
                (
                    "file",
                    models.FileField(
                        storage=ram.utils.DeduplicatedStorage(), upload_to="files/"
                    ),
                ),
                ("creation_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("private", models.BooleanField(default=True, editable=False)),
                ("notes", tinymce.models.HTMLField(blank=True)),
                (
                    "book",
                    models.ManyToManyField(
                        blank=True, related_name="invoice", to="bookshelf.basebook"
                    ),
                ),
                (
                    "rolling_stock",
                    models.ManyToManyField(
                        blank=True, related_name="invoice", to="roster.rollingstock"
                    ),
                ),
            ],
            options={
                "verbose_name": "Invoice",
                "verbose_name_plural": "Invoices",
            },
        ),
    ]
