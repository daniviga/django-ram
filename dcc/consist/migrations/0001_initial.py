# Generated by Django 4.0.2 on 2022-04-02 14:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('roster', '0001_initial'),
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consist',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=128)),
                ('address', models.SmallIntegerField(blank=True, default=None, null=True)),
                ('epoch', models.CharField(blank=True, max_length=32)),
                ('notes', models.TextField(blank=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.company')),
                ('tags', models.ManyToManyField(blank=True, related_name='consist', to='metadata.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='ConsistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('consist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consist.consist')),
                ('rolling_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roster.rollingstock')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
