# Generated by Django 5.1.1 on 2024-10-30 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_maker', '0010_courses_available_material_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='course_level',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Level 1 - Basic implementation'), (2, 'Level 2 - Rudimentary implementation'), (3, 'Level 3 - Crucial implementation'), (4, 'Level 4 - Key implementation'), (5, 'Level 5 - Substantial implementation'), (6, 'Level 6 - Critical implementation'), (7, 'Level 7 - Leading implementation'), (8, 'Level 8 - Specialist implementation'), (9, 'Level 9 - Innovative implementation')], default=1, verbose_name='Course Level'),
        ),
        migrations.AlterField(
            model_name='courses',
            name='content_lang',
            field=models.CharField(choices=[('EN', 'English'), ('FR', 'French'), ('ES', 'Spanish'), ('DE', 'German'), ('UR', 'Urdu')], default='EN', max_length=2, verbose_name='Content Language'),
        ),
        migrations.AlterField(
            model_name='courses',
            name='course_description',
            field=models.TextField(verbose_name='Description of course'),
        ),
    ]
