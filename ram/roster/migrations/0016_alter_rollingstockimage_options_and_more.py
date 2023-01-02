# Generated by Django 4.1.3 on 2023-01-02 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0015_alter_rollingstockimage_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="rollingstockimage",
            options={"ordering": ["order"]},
        ),
        migrations.AddField(
            model_name="rollingstockimage",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
