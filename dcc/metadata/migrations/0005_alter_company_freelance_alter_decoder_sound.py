# Generated by Django 4.0.2 on 2022-04-02 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_company_freelance_decoder_sound'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='freelance',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='decoder',
            name='sound',
            field=models.BooleanField(default=False),
        ),
    ]
