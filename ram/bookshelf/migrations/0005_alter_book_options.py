# Generated by Django 4.2.5 on 2023-10-03 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookshelf", "0004_rename_numbers_of_pages_book_number_of_pages"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["authors__last_name", "title"]},
        ),
    ]
