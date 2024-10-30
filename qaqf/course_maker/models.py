import os
import PyPDF2
from docx import Document
from django.db import models



def upload_to(instance, filename):
    # Store files in a directory named after the course ID
    course_id = instance.course.id
    return f"media/{course_id}/{filename}"


class Courses(models.Model):
    COURSE_TYPE_CHOICES = [
        ('Pre-Recorded', 'Pre-Recorded'),
        ('Live Webinar', 'Live Webinar'),
        ('Hybrid', 'Hybrid')
    ]

    KNOWLEDGE_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Middle', 'Middle'),
        ('Senior', 'Senior')
    ]

    PRACTICE_CHOICES = [
        ('Light', 'Light'),
        ('Moderate', 'Moderate'),
        ('Intensive', 'Intensive')
    ]

    DURATION_CHOICES = [
        ('1', '1 week'),
        ('2', '2 weeks'),
        ('3', '3 weeks'),
        ('4', '4 weeks')
    ]

    CONTENT_LANG_CHOICES = [
        ('EN', 'English'),
        ('FR', 'French'),
        ('ES', 'Spanish'),
        ('DE', 'German'),
        ('UR', 'Urdu'),

        # Add more language options as needed
    ]
    # Level Descriptors
    LEVEL_CHOICES = [
        (1, 'Level 1 - Basic implementation'),
        (2, 'Level 2 - Rudimentary implementation'),
        (3, 'Level 3 - Crucial implementation'),
        (4, 'Level 4 - Key implementation'),
        (5, 'Level 5 - Substantial implementation'),
        (6, 'Level 6 - Critical implementation'),
        (7, 'Level 7 - Leading implementation'),
        (8, 'Level 8 - Specialist implementation'),
        (9, 'Level 9 - Innovative implementation')
    ]
    # Basic Course Details
    course_title = models.CharField(max_length=200)
    course_description = models.TextField("Description of course")
    participants_info = models.TextField("Participants and their goals")
    prerequisite_knowledge = models.TextField("Pre-requisite Knowledge")
    course_level = models.PositiveSmallIntegerField("Course Level", choices=LEVEL_CHOICES, default=1,null=True, blank=True)

    # Enum/Choice Fields
    content_lang = models.CharField("Content Language", max_length=2, choices=CONTENT_LANG_CHOICES, default='EN')
    course_type = models.CharField("Course Type", max_length=15, choices=COURSE_TYPE_CHOICES)
    knowledge_level = models.CharField("Knowledge Level", max_length=8, choices=KNOWLEDGE_LEVEL_CHOICES)
    duration = models.CharField("Duration (in weeks)", max_length=1, choices=DURATION_CHOICES)
    practice = models.CharField("Practice Intensity", max_length=9, choices=PRACTICE_CHOICES)

    # Boolean Fields
    optimized_for_mooc = models.BooleanField("MOOC Optimized", default=False)
    project_based = models.BooleanField("Project Based", default=False)
    assignment = models.BooleanField("Assignment Prototypes", default=False)
    long_course_support = models.BooleanField("Long Course Support", default=False)


    def __str__(self):
        return self.course_title

    def get_full_language_name(self,language_key):

        return dict(self.CONTENT_LANG_CHOICES).get(language_key, 'English')


class CourseMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('textbook', 'Textbook'),
        ('helping', 'Helping Material')
    ]

    course = models.ForeignKey(Courses, related_name='course_materials', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_to)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, null=True, blank=True)  # E.g., 'pdf', 'txt', 'docx'
    file_content = models.TextField("Extracted Content", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_type = self.get_file_type()
            self.extract_file_content()
        super().save(*args, **kwargs)

    def get_file_type(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower().replace('.', '')  # Return the file extension

    def extract_file_content(self):
        if self.file_type == 'pdf':
            self.file_content = self.extract_pdf_content()
        elif self.file_type in ['doc', 'docx']:
            self.file_content = self.extract_word_content()
        elif self.file_type == 'txt':
            self.file_content = self.extract_txt_content()

    def extract_pdf_content(self):
        try:
            pdf_reader = PyPDF2.PdfReader(self.file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

    def extract_word_content(self):
        try:
            doc = Document(self.file)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            return f"Error reading Word file: {e}"

    def extract_txt_content(self):
        try:
            return self.file.read().decode('utf-8')
        except Exception as e:
            return f"Error reading TXT file: {e}"

    def __str__(self):
        return f"{self.material_type.capitalize()} - {self.original_filename}"



# Additional Models for Content, Quizzes, and other steps
class LearningOutcome(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='learning_outcomes')
    outcome = models.TextField("Learning Outcome")
    tag = models.CharField("Tag", max_length=3)
    number = models.IntegerField()
    sub_items = models.JSONField(default=list)  # Sub-items, e.g., ['A1', 'A2', ...]


class ContentListing(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='content_listings')
    content_item = models.TextField("Content Item")
    serial_number = models.CharField(max_length=100)


class Content(models.Model):

    content_listing = models.ForeignKey(ContentListing, on_delete=models.CASCADE, related_name='contents')

    TYPE_CHOICES = [
        ('Video', 'Video'),
        ('Reading', 'Reading')
    ]

    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    material = models.FileField(upload_to='content_materials/', null=True, blank=True)
    duration = models.IntegerField("Duration (in minutes)", null=True, blank=True)
    key_points = models.TextField(null=True, blank=True)  # Allow null values for key_points
    script = models.TextField("Script", null=True, blank=True)


class Quiz(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='quizzes')

    QUESTION_TYPE_CHOICES = [
        ('Single Choice', 'Single Choice'),
        ('Multiple Choice', 'Multiple Choice')
    ]

    question = models.TextField("Question")
    type = models.CharField(max_length=15, choices=QUESTION_TYPE_CHOICES)
    correct_option = models.IntegerField()
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
