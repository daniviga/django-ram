# Generated by Django 4.0 on 2021-12-20 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0001_initial'),
        ('roster', '0014_alter_company_options_alter_cab_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decoder',
            name='manufacturer',
        ),
        migrations.AlterField(
            model_name='cab',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.company'),
        ),
        migrations.AlterField(
            model_name='cab',
            name='decoder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.decoder'),
        ),
        migrations.AlterField(
            model_name='cab',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.manufacturer'),
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='Decoder',
        ),
        migrations.DeleteModel(
            name='Manufacturer',
        ),
    ]
