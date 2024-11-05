import os
import shutil
from django.test import TestCase
from django.core.files import File
from rest_framework import status
from rest_framework.test import APIClient
from PyPDF2 import PdfReader
from pydub import AudioSegment
from course_maker.models import Courses
from course_material.models import CourseMaterial
APP_FOLDER = os.path.dirname(os.path.dirname(__file__))  # Adjust this to point to app_folder
TEST_FILES_DIR = os.path.join(os.path.dirname(APP_FOLDER), 'media/sample_books')
test_file=TEST_FILES_DIR

class CourseMaterialAPITests(TestCase):
    def setUp(self):
        # Create a test course
        try:
            self.course = Courses.objects.create(
            course_title="Test Course",
            course_description="A test course.",
            content_lang="EN",
            course_type="Pre-Recorded",
            knowledge_level="Beginner",
            prerequisite_knowledge="None",
            participants_info="General public",
            duration="1",
            practice="Light",
            optimized_for_mooc=False,
            project_based=False,
            assignment=False,
            long_course_support=False,
            course_level=1
        )
        except Exception as e:
            print(e)
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
                file_content = "\n".join(
                [page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            )

        self.url = f'http://127.0.0.1:8000/api/course-materials/'
        self.client = APIClient()

    def tearDown(self):
        path = os.path.join(os.path.dirname(APP_FOLDER), f'media\\media\\{self.course.id}')
        # Cleanup code to delete the folder and all its contents
        if os.path.exists(path):
            shutil.rmtree(path)


    def test_create_course_material_pdf(self):
        # Test creating a new CourseMaterial with a PDF file
        # Set the file path and file name
        file_path = os.path.join(TEST_FILES_DIR, 'python.pdf')
        file_name = os.path.basename(file_path)
        with open(file_path,'rb') as pdf_file:
            response = self.client.post(
                self.url,
                {
                    'course': self.course.id,
                    'file': pdf_file,
                    'file_type': 'pdf',
                    'material_type': 'textbook',
                    'original_filename':file_name
                },
                format='multipart'
            )
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        material = CourseMaterial.objects.get(id=response.data['id'])
        self.assertEqual(material.course, self.course)

        self.assertEqual(material.file_type, 'pdf')
        self.assertIsNotNone( material.file_content)

    def test_list_course_materials(self):

        # List course materials
        url = self.url+str(self.course.id)+"/"
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)

    def test_retrieve_course_material(self):

        # Retrieve the material
        url=self.url+str(self.material.id)+"/"
        response = self.client.get(url)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.material.id)
        self.assertEqual(response.data['file_type'], 'pdf')
        self.assertIsNotNone(response.data['file_content'])


    def test_update_course_material(self):
        url = self.url+str(self.material.id)+"/"
        with open(os.path.join(TEST_FILES_DIR, 'python_updated.pdf'), 'rb') as updated_pdf_file:

            response = self.client.patch(
                url,
                {
                    'file': updated_pdf_file,
                    'material_type': 'helping'
                },
                format='multipart'
            )

        # Refresh from database
        self.material.refresh_from_db()

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.material.file_type, 'pdf')
        self.assertIsNotNone(self.material.file_content)
        self.assertEqual(self.material.material_type,'helping')

    def test_delete_course_material(self):
        url = self.url + str(self.material.id) + "/"
        response = self.client.delete(url)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMaterial.objects.filter(pk=self.material.id).exists())  # Confirm deletion

    def test_download_audio_from_youtube(self):
        # Test downloading audio directly from YouTube
        response = self.client.post(self.url, {
            'course': self.course.id,
            'audio_book':"https://www.youtube.com/watch?v=BZP1rYjoBgI",
            'material_type': 'helping',
            'file_type':'audiobook',
        })

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        material = CourseMaterial.objects.get(id=response.data['id'])
        self.assertEqual(material.file_type, 'audiobook')
        self.assertIsNotNone( material.file_content)



    # ToDo
    # Complete these tests when resources are available.
    # def _test_download_audio_from_aws_s3(self):
    #     # Test downloading an audio file directly from AWS S3
    #     response = self.client.post(self.url, {
    #         'course': self.course.id,
    #         'audio_book': "s3://bucket-name/path/to/sample_audio.mp3",
    #         'material_type': 'helping'
    #     })
    #
    #     # Assertions
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     material = CourseMaterial.objects.get(id=response.data['id'])
    #     self.assertEqual(material.file_type, 'audiobook')
    #
    # def _test_download_audio_from_general_url(self):
    #     # Test downloading audio file from a general URL
    #     response = self.client.post(self.url, {
    #         'course': self.course.id,
    #         'audio_book': "https://example.com/sample_audio.mp3",
    #         'material_type': 'helping'
    #     })
    #
    #     # Assertions
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     material = CourseMaterial.objects.get(id=response.data['id'])
    #     self.assertEqual(material.file_type, 'audiobook')