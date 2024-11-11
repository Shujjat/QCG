import os
from django.conf import settings
from django.core.files import File
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from PyPDF2 import PdfReader
from course_maker.models import Courses
from course_material.models import CourseMaterial
from llm.questions_model import UserQuestionLog
from llm.llm import LLM

# Constants
APP_FOLDER = os.path.dirname(os.path.dirname(__file__))
TEST_FILES_DIR = os.path.join(os.path.dirname(APP_FOLDER), 'media/sample_books')
test_file = TEST_FILES_DIR


class MakiViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Initialize LLM instance once for all tests
        cls.llm = LLM()

    def setUp(self):
        # Set up a dummy user and course
        self.dummy_user = User.objects.create_user(username="dummy_user", password="dummy_password")
        self.client.login(username="dummy_user", password="dummy_password")

        # Set up the course
        pdf_path = os.path.join(settings.BASE_DIR, 'media/sample_books/python.pdf')
        with open(pdf_path, 'rb') as pdf_file:
            self.course = Courses.objects.create(
                course_title="Python Programming",
                course_description="Learn the basics of Python programming.",
                content_lang="EN",
                course_type="Pre-Recorded",
                knowledge_level="Senior",
                prerequisite_knowledge="Basic programming",
                participants_info="For students and professionals",
                duration="2",
                practice="Intensive",
                optimized_for_mooc=True,
                project_based=True,
                assignment=True,
                long_course_support=False,
            )

        # Set up course material
        file_path = os.path.join(TEST_FILES_DIR, 'python.pdf')
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            file_content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            self.material = CourseMaterial.objects.create(
                course=self.course,
                file=File(pdf_file, file_name),
                file_type='pdf',
                material_type="textbook",
                original_filename=file_name,
                file_content=file_content
            )

        # Set up URL for the test
        self.url = 'http://127.0.0.1:8000/api/ask_maki/ask_maki/'

    def test_ask_maki_text_response(self):
        """
        Test POST request for text-only response.
        """
        data = {
            'course_id': self.course.id,
            'user_question': 'What is Python?',
            'as_audio': False
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_id'], self.course.id)
        self.assertEqual(response.data['course_title'], self.course.course_title)
        self.assertIn('response', response.data)

    def test_ask_maki_audio_response(self):
        """
        Test POST request for audio response.
        """
        data = {
            'course_id': self.course.id,
            'user_question': 'Explain Python basics.',
            'as_audio': True
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('audio_url', response.data)
        print("Audio URL:", response.data['audio_url'])

    def test_ask_maki_custom_voice_audio(self):
        """
        Test POST request for audio response with custom voice, rate, and volume.
        """
        data = {
            'course_id': self.course.id,
            'user_question': 'Tell me about Python data types.',
            'as_audio': True,
            'voice_name': 'David',
            'rate': 150,
            'volume': 0.8
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('audio_url', response.data)
        print("Custom Voice Audio URL:", response.data['audio_url'])

    def test_invalid_course_id(self):
        """
        Test with invalid course ID.
        """
        data = {
            'course_id': 999,
            'user_question': 'What is this course about?',
            'as_audio': False
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Course not found.")

    def test_missing_user_question(self):
        """
        Test with missing user question.
        """
        data = {
            'course_id': self.course.id,
            'as_audio': False
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "user_question is required.")



    def test_log_creation(self):
        """
        Test if log entry is created successfully.
        """
        data = {
            'course_id': self.course.id,
            'user_question': 'What is Python?',
            'as_audio': False
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log_exists = UserQuestionLog.objects.filter(user_question=data['user_question']).exists()
        self.assertTrue(log_exists)
