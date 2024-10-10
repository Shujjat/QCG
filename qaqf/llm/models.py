# models.py

from django.db import models
from django.utils import timezone

class Log(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    function_name = models.CharField(max_length=255)
    course_id = models.IntegerField(null=True, blank=True)
    input_data = models.TextField(null=True, blank=True)
    output_data = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.function_name} - {self.timestamp}"
