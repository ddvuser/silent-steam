# Generated by Django 5.0.3 on 2024-04-05 12:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('due_date', models.DateField()),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.class')),
            ],
        ),
    ]
