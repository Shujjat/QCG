from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from course_maker.models import Courses,LearningOutcome

class LearningOutcomeAPITest(APITestCase):
    def setUp(self):
        # Create a course and learning outcome
        self.course = Courses.objects.create(course_title="Advanced Django", course_description="A course on Django")
        self.learning_outcome = LearningOutcome.objects.create(
            course=self.course, outcome="Understand Django ORM", tag="ORM", number=1, sub_items=["A1", "A2"]
        )
        self.url = f'http://127.0.0.1:8000/api/course/{self.course.id}/learning_outcomes/'
    def test_get_learning_outcome(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_learning_outcome(self):
        data = {"outcome": "Learn Django ORM"}
        response = self.client.patch(self.url, data, format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.learning_outcome.refresh_from_db()
        self.assertEqual(self.learning_outcome.outcome, "Learn Django ORM")
