from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from course_maker.models import Courses, CourseMaterial

class CourseMaterialAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a sample course
        self.course = Courses.objects.create(
            course_title="Advanced Django",
            course_description="A comprehensive course on Django.",
            content_lang="EN",
            course_type="Pre-Recorded",
            knowledge_level="Senior",
            prerequisite_knowledge="Basic Django",
            participants_info="Software Engineers",
            duration="2",
            practice="Intensive",
            optimized_for_mooc=True,
            project_based=True,
            assignment=True,
            long_course_support=False
        )

        # Sample file for upload
        self.sample_pdf = SimpleUploadedFile("sample.pdf", b"PDF content", content_type="application/pdf")

        # URL for the course material API
        self.url = reverse('course-materials', kwargs={'course_id': self.course.id})

    def test_upload_course_material(self):
        """Test uploading a course material file."""
        data = {
            'file': self.sample_pdf,
            'material_type': 'textbook'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
        self.assertIn('material_type', response.data)

    def test_get_course_material_list(self):
        """Test retrieving a list of course materials."""
        # Upload a material first
        CourseMaterial.objects.create(
            course=self.course,
            file=self.sample_pdf,
            material_type='textbook',
            extracted_content='Sample content from PDF'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least one material should be returned
        self.assertIn('file', response.data[0])
        self.assertIn('extracted_content', response.data[0])

    def test_get_single_course_material(self):
        """Test retrieving a single course material."""
        material = CourseMaterial.objects.create(
            course=self.course,
            file=self.sample_pdf,
            material_type='textbook',
            extracted_content='Sample content from PDF'
        )

        url = reverse('course-material-detail', kwargs={'course_id': self.course.id, 'material_id': material.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file'], material.file.name)
        self.assertEqual(response.data['extracted_content'], material.extracted_content)

    def test_update_course_material(self):
        """Test updating a course material."""
        material = CourseMaterial.objects.create(
            course=self.course,
            file=self.sample_pdf,
            material_type='textbook',
            extracted_content='Sample content from PDF'
        )

        url = reverse('course-material-detail', kwargs={'course_id': self.course.id, 'material_id': material.id})
        data = {
            'material_type': 'helping'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        material.refresh_from_db()
        self.assertEqual(material.material_type, 'helping')

    def test_delete_course_material(self):
        """Test deleting a course material."""
        material = CourseMaterial.objects.create(
            course=self.course,
            file=self.sample_pdf,
            material_type='textbook',
            extracted_content='Sample content from PDF'
        )

        url = reverse('course-material-detail', kwargs={'course_id': self.course.id, 'material_id': material.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMaterial.objects.filter(id=material.id).exists())

    def test_invalid_material_upload(self):
        """Test invalid material upload."""
        invalid_file = SimpleUploadedFile("invalid.txt", b"Invalid content", content_type="text/plain")
        data = {
            'file': invalid_file,
            'material_type': 'unknown'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extracted_content_on_material_upload(self):
        """Test if extracted content is properly saved on material upload."""
        data = {
            'file': self.sample_pdf,
            'material_type': 'textbook'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        material_id = response.data['id']
        material = CourseMaterial.objects.get(id=material_id)

        # Check that extracted content is stored
        self.assertTrue(material.extracted_content)
        self.assertIn('PDF content', material.extracted_content)
