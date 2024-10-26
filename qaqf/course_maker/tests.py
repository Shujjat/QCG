from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Courses
class CourseCreationWizardTest(APITestCase):
    def setUp(self):
        try:
            self.course = Courses.objects.create(
                course_title="Setup Advanced Django",
                course_description="An in-depth course on Django.",
                content_lang="EN",
                course_type="Pre-Recorded",
                knowledge_level="Senior",
                prerequisite_knowledge="prerequisite_knowledge",
                participants_info="participants_info",
                duration="2",
                practice="Intensive",
                optimized_for_mooc=True,
                project_based=True,
                assignment=True,
                long_course_support=False
            )
            print("Course created successfully:", self.course)
        except Exception as e:
            print("Error creating course:", str(e))

        self.url = 'http://127.0.0.1:8000/api/courses/'
    def test_update_course(self):
        url = f"{self.url}{self.course.id}/"
        print(url)
        data = {
            "course_title": "New Title",
            "course_description": "Updated description."
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.course_title, "New Title")
        self.assertEqual(self.course.course_description, "Updated description.")
    def test_create_course(self):

        data = {
            "course_title": "Advanced Django",
            "course_description": "An in-depth course on Django.",
            "content_lang": "EN",
            "course_type": "Pre-Recorded",
            "knowledge_level": "Senior",
            'prerequisite_knowledge':'prerequisite_knowledge',
            "participants_info":"participants_info",
            "duration": "2",
            "practice": "Intensive",
            "optimized_for_mooc": True,
            "project_based": True,
            "assignment": True,
            "long_course_support": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course_title'], data['course_title'])

    def test_get_course_detail(self):
        url = f'{self.url}{self.course.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_title'], self.course.course_title)

    def test_delete_course(self):
        url =f'{self.url}{self.course.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Courses.objects.filter(id=self.course.id).exists())

    def test_get_all_courses(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)