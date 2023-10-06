# Generated by Django 4.2.5 on 2023-10-01 20:16

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("metadata", "0012_alter_decoder_manufacturer_decoderdocument"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
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
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("ISBN", models.CharField(max_length=13, unique=True)),
                ("publication_year", models.SmallIntegerField(blank=True, null=True)),
                ("purchase_date", models.DateField(blank=True, null=True)),
                ("notes", ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ("creation_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("authors", models.ManyToManyField(to="bookshelf.author")),
            ],
        ),
        migrations.CreateModel(
            name="Publisher",
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
                ("name", models.CharField(max_length=200)),
                ("website", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="BookProperty",
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
                ("value", models.CharField(max_length=256)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="property",
                        to="bookshelf.book",
                    ),
                ),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="metadata.property",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Properties",
            },
        ),
        migrations.AddField(
            model_name="book",
            name="publisher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bookshelf.publisher"
            ),
        ),
        migrations.AddField(
            model_name="book",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="bookshelf", to="metadata.tag"
            ),
        ),
    ]
