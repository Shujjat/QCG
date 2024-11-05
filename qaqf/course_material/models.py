from django.db import models
from course_maker.models import Courses

def upload_to(instance, filename):
    # Store files in a directory named after the course ID
    course_id = instance.course.id
    return f"media/{course_id}/{filename}"


class CourseMaterial(models.Model):

    MATERIAL_TYPE_CHOICES = [
        ('textbook', 'Textbook'),
        ('helpingbook', 'Helping Book')

    ]
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('txt', 'Text'),
        ('doc', 'Word'),
        ('audiobook','AudioBook')

    ]

    course = models.ForeignKey(Courses, related_name='course_materials', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_to,blank=True,null=True)
    original_filename = models.CharField(max_length=255,null=True, blank=True)
    file_type = models.CharField(max_length=10,choices=FILE_TYPE_CHOICES)  # E.g., 'pdf', 'txt', 'docx'
    file_content = models.TextField("File Content", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES)
    audio_book = models.URLField("Audio Book URL", null=True, blank=True)

    def __str__(self):
        return f"{self.material_type.capitalize()} - {self.original_filename}"
