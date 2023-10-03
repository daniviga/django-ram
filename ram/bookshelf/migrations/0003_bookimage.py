# Generated by Django 4.2.5 on 2023-10-02 10:36

from django.db import migrations, models
import django.db.models.deletion
import ram.utils


class Migration(migrations.Migration):

    dependencies = [
        ("bookshelf", "0002_book_language_book_numbers_of_pages_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BookImage",
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
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=ram.utils.DeduplicatedStorage,
                        upload_to="images/books/",
                    ),
                ),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="image",
                        to="bookshelf.book",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
                "abstract": False,
            },
        ),
    ]
