# Generated by Django 4.0.3 on 2022-04-08 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0002_alter_rollingstockimage_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rollingstockimage',
            name='rolling_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thumbnail', to='roster.rollingstock'),
        ),
    ]