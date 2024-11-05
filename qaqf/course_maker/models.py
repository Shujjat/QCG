from django.db import models
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
    # New fields for Step 2

    course_level = models.PositiveSmallIntegerField("Course Level", choices=LEVEL_CHOICES, default=1, null=True,
                                                    blank=True)


    def __str__(self):
        return self.course_title

    def get_full_language_name(self,language_key):

        return dict(self.CONTENT_LANG_CHOICES).get(language_key, 'English')



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
