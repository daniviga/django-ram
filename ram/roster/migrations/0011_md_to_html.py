# Generated by Django 4.1 on 2022-08-24 15:30

import markdown
from django.db import migrations


def md_to_html(apps, schema_editor):
    fields = {
        "RollingStock": ["notes"],
    }

    for m in fields.items():
        model = apps.get_model("roster", m[0])

        for row in model.objects.all():
            for field in m[1]:
                html = markdown.markdown(getattr(row, field))
                row.__dict__[field] = html

            row.save(update_fields=m[1])


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0010_alter_rollingstock_notes"),
    ]

    operations = [
        migrations.RunPython(
            md_to_html,
            reverse_code=migrations.RunPython.noop
        ),
    ]
