# Generated by Django 5.0.3 on 2024-04-05 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_submission'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.FloatField()),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.submission')),
            ],
        ),
    ]
