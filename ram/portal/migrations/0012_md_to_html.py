# Generated by Django 4.1 on 2022-08-24 15:00

import markdown
from django.db import migrations


def md_to_html(apps, schema_editor):
    fields = {
        "SiteConfiguration": ["about", "footer", "footer_extended"],
        "Flatpage": ["content"]
    }

    for m in fields.items():
        model = apps.get_model("portal", m[0])

        for row in model.objects.all():
            for field in m[1]:
                html = markdown.markdown(getattr(row, field))
                row.__dict__[field] = html

            row.save(update_fields=m[1])


class Migration(migrations.Migration):

    dependencies = [
        (
            "portal",
            "0011_alter_flatpage_content_alter_siteconfiguration_about_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            md_to_html,
            reverse_code=migrations.RunPython.noop
        ),
    ]
