# Generated by Django 5.1.1 on 2024-10-05 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_maker', '0006_learningoutcome_sub_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='key_points',
            field=models.TextField(blank=True, null=True),
        ),
    ]
