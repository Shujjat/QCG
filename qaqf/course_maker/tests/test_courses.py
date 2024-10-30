import os
from django.conf import settings
from django.core.files import File
from rest_framework.test import APITestCase
from rest_framework import status
from course_maker.models import Courses
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class CourseCreationWizardTest(APITestCase):
    def setUp(self):
        try:
            pdf_path = os.path.join(settings.BASE_DIR, 'media/sample_books/python.pdf')
            with open(pdf_path, 'rb') as pdf_file:
                file = File(pdf_file, name='python.pdf')

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
                    long_course_support=False,
                    course_level=1,
                    available_material=file
                    )
            logger.info("Course created successfully:", self.course)
            logger.info("::::::::::::::::::::::::: self.course.available_material_content:::::::::::::::::::::::::::::")
            logger.info( self.course.available_material_content)
        except Exception as e:
            logger.info("Error creating course:", str(e))

        self.url = 'http://127.0.0.1:8000/api/courses/'
    def test_update_course(self):
        url = f"{self.url}{self.course.id}/"
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
        self.assertIsNotNone(self.course.available_material)
        self.assertTrue(self.course.available_material.name.endswith('.pdf'))

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