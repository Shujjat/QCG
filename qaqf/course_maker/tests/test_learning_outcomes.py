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

    def test_create_learning_outcome(self):
        data = {
            "outcome": "Understand Django basics",
            "tag": "A",
            "number": 1,
            "sub_items": ["A1", "A2"]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearningOutcome.objects.count(), 1)
        created_outcome = LearningOutcome.objects.first()
        self.assertEqual(created_outcome.outcome, "Understand Django basics")

    def test_update_learning_outcome(self):
        # Prepare the payload as a list of dictionaries
        data = [
            {
                "id": self.learning_outcome.id,  # Include the ID of the learning outcome
                "outcome": "Learn Django ORM"
            }
        ]

        # Send the PATCH request
        response = self.client.patch(self.url, data, format='json')


        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the learning outcome from the database and check the updated value
        self.learning_outcome.refresh_from_db()
        self.assertEqual(self.learning_outcome.outcome, "Learn Django ORM")
    #
    # def test_delete_learning_outcome(self):
    #     response = self.client.delete(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(LearningOutcome.objects.count(), 0)

    # def test_list_learning_outcomes(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)
    #     self.assertEqual(response.data[0]['outcome'], "Understand Django ORM")
    #     self.assertEqual(response.data[1]['outcome'], "Understand Django Views")

    #
    # def test_view_learning_outcome(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['outcome'], "Understand Django ORM")
    #     self.assertEqual(response.data['tag'], "A")
    #     self.assertEqual(response.data['number'], 1)
    #     self.assertEqual(response.data['sub_items'], ["A1", "A2"])