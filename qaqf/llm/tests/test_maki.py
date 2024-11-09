import os
from django.conf import settings
from django.core.files import File
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from PyPDF2 import PdfReader
#############################################
from course_maker.models import Courses
from course_material.models import CourseMaterial
from llm.questions_model import UserQuestionLog
from llm.llm import LLM
APP_FOLDER = os.path.dirname(os.path.dirname(__file__))  # Adjust this to point to app_folder
TEST_FILES_DIR = os.path.join(os.path.dirname(APP_FOLDER), 'media/sample_books')
test_file=TEST_FILES_DIR


class MakiViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Initialize LLM instance once for all tests
        cls.llm = LLM()

    def setUp(self):
        # Set up a dummy user and course
        self.dummy_user = User.objects.create_user(username="dummy_user", password="dummy_password")
        pdf_path = os.path.join(settings.BASE_DIR, 'media/sample_books/python.pdf')
        with open(pdf_path, 'rb') as pdf_file:
            self.course = Courses.objects.create(
                course_title="Python Programming",
                course_description="",
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

            )
        file_path = os.path.join(TEST_FILES_DIR, 'python.pdf')
        file_name = os.path.basename(file_path)

        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            self.material = CourseMaterial.objects.create(
                course=self.course,
                file=File(pdf_file, file_name),
                file_type=pdf_file.name.split('.')[-1].lower(),
                material_type="textbook",
                original_filename=file_name,
                file_content="\n".join(
                    [page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            )

        self.url = f'http://127.0.0.1:8000/api/ask_maki/ask_maki/'

    def test_ask_maki_get_request(self):
        """
        Test the GET request to `ask_maki` to ensure it renders HTML form.
        """

        response = self.client.get(self.url)

        # Check for a 200 status code and expected content type for an HTML form
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_ask_maki_post_request_success(self):
        """
        Test the POST request to `ask_maki` to ensure it processes correctly.
        """


        # Sample question data
        data = {
            'course_id': self.course.id,
            'user_question': 'What is this course about?'
        }

        # Make POST request
        response = self.client.post(self.url, data, format='json')

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response data contains the course_id, course_title, and response
        self.assertEqual(response.data['course_id'], self.course.id)
        self.assertEqual(response.data['course_title'], self.course.course_title)
        self.assertIn('response', response.data)

        # Check that a UserQuestionLog entry was created
        self.assertTrue(UserQuestionLog.objects.filter(user_question=data['user_question']).exists())

    def test_ask_maki_post_request_missing_course_id(self):
        """
        Test the POST request to `ask_maki` when course_id is missing.
        """


        # Data without course_id
        data = {
            'user_question': 'What is this course about?'
        }

        # Make POST request
        response = self.client.post(self.url, data, format='json')

        # Check for a 400 Bad Request response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "course_id is required.")

    def test_ask_maki_post_request_invalid_course_id(self):
        """
        Test the POST request to `ask_maki` with an invalid course_id.
        """


        # Data with an invalid course_id
        data = {
            'course_id': 999,  # Nonexistent course_id
            'user_question': 'What is this course about?'
        }

        # Make POST request
        response = self.client.post(self.url, data, format='json')

        # Check for a 404 Not Found response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Course not found.")
