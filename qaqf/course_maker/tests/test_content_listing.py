from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from course_maker.models import Courses, ContentListing


class ContentListingAPITestCase(APITestCase):

    def setUp(self):
        # Create a Course to associate with ContentListing
        self.course = Courses.objects.create(
            course_title="Test Course",
            course_description="Description of the test course",
            participants_info="Test participants info",
            prerequisite_knowledge="Basic Python",
            course_type="Pre-Recorded",
            knowledge_level="Beginner",
            duration="1",
            practice="Light",
            content_lang="EN",
        )

        # URL for the ContentListing endpoint
        self.url = reverse('contentlisting-list')  # Assuming 'contentlisting-list' is the URL name

        # Create a ContentListing for tests
        self.content_listing = ContentListing.objects.create(
            course=self.course,
            content_item="First Content",
            serial_number="SN001"
        )

    def test_create_content_listing(self):
        data = {
            'course': self.course.id,
            'content_item': 'New Content Item',
            'serial_number': 'SN002'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContentListing.objects.count(), 2)
        self.assertEqual(ContentListing.objects.last().content_item, 'New Content Item')

    def test_update_content_listing(self):
        content_listing_url = reverse('contentlisting-detail', args=[self.content_listing.id])
        data = {
            'course':self.course.id,
            'content_item': 'Updated Content Item',
            'serial_number': 'SN001U'
        }
        response = self.client.put(content_listing_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content_listing.refresh_from_db()
        self.assertEqual(self.content_listing.content_item, 'Updated Content Item')
        self.assertEqual(self.content_listing.serial_number, 'SN001U')

    def test_delete_content_listing(self):
        content_listing_url = reverse('contentlisting-detail', args=[self.content_listing.id])
        response = self.client.delete(content_listing_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ContentListing.objects.count(), 0)

    def test_list_all_content_listings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # We only have 1 content listing from setUp
        self.assertEqual(response.data[0]['content_item'], self.content_listing.content_item)

    def test_view_specific_content_listing(self):
        content_listing_url = reverse('contentlisting-detail', args=[self.content_listing.id])
        response = self.client.get(content_listing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content_item'], self.content_listing.content_item)
        self.assertEqual(response.data['serial_number'], self.content_listing.serial_number)
