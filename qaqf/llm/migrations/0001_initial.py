# Generated by Django 5.1.1 on 2024-10-10 06:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('function_name', models.CharField(max_length=255)),
                ('course_id', models.IntegerField(blank=True, null=True)),
                ('input_data', models.TextField(blank=True, null=True)),
                ('output_data', models.TextField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
            ],
        ),
    ]