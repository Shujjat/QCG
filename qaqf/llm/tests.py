import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qaqf.settings')

from django.test import TestCase
from llm.llm import LLM
from course_maker.models import Courses


class TestLLM(TestCase):

    def setUp(self):
        # Initialize the LLM class
        self.llm = LLM()
        self.course_id = 1  # Use an actual course ID from your database
        self.item_id = 123  # Use an actual item ID if required

        # Retrieve an actual course from the database (replace with a valid course)
        # try:
        #     self.course = Courses.objects.get(pk=self.course_id)
        # except Courses.DoesNotExist:
        #     self.skipTest(f"Course with ID {self.course_id} does not exist.")

    def test_generate_course_title_and_description(self):
        # Call the actual generate_course_title_and_description method
        title, description = self.llm.generate_course_title_and_description(self.course_id)

        # Print the output to observe the result
        print("Generated Course Title:", title)
        print("Generated Course Description:", description)

        # Basic assertions to check if title and description are not empty
        self.assertTrue(len(title) > 0, "Course title should not be empty.")
        self.assertTrue(len(description) > 0, "Course description should not be empty.")

    # def test_generate_learning_outcomes(self):
    #     # Call the actual generate_learning_outcomes method
    #     learning_outcomes = self.llm.generate_learning_outcomes(self.course_id, self.item_id)
    #
    #     # Print the output to observe the result
    #     print("Generated Learning Outcomes:", learning_outcomes)
    #
    #     # Basic assertions to check if learning outcomes are returned
    #     self.assertTrue(len(learning_outcomes) > 0, "Learning outcomes should not be empty.")
    #
    #     # Ensure each learning outcome has a tag and sub-items
    #     for outcome in learning_outcomes:
    #         self.assertIn("tag", outcome)
    #         self.assertIn("outcome", outcome)
    #         self.assertIn("sub_items", outcome)
    #
    # def test_generate_content_listing(self):
    #     # Call the actual generate_content_listing method
    #     content_listing = self.llm.generate_content_listing(self.course_id, self.item_id)
    #
    #     # Print the output to observe the result
    #     print("Generated Content Listing:", content_listing)
    #
    #     # Basic assertions to check if content listing is returned
    #     self.assertTrue(len(content_listing) > 0, "Content listing should not be empty.")
    #
    #     # Ensure content listing has modules and items
    #     self.assertIn("Module", content_listing)
    #
    # def test_create_chunks(self):
    #     text = "This is a long piece of text that needs to be split into smaller chunks for processing. Each chunk will be 10 words."
    #     chunk_size = 10
    #     expected_chunks = [
    #         "This is a long piece of text that needs to be split",
    #         "into smaller chunks for processing. Each chunk will be",
    #         "10 words."
    #     ]
    #
    #     chunks = self.llm.create_chunks(text, chunk_size)
    #
    #     # Print the output to observe the result
    #     print("Created Chunks:", chunks)
    #
    #     # Assertions to check if the text is chunked correctly
    #     self.assertEqual(chunks, expected_chunks)
    #
    # def test_extract_learning_outcomes(self):
    #     generated_text = """
    #     - Outcome A: Learn Python basics
    #         - A1: Understand variables
    #         - A2: Write basic functions
    #     - Outcome B: Advanced Python
    #         - B1: Master classes and objects
    #         - B2: Work with modules
    #     """
    #     expected_outcomes = [
    #         {
    #             "tag": "A",
    #             "outcome": "Learn Python basics",
    #             "sub_items": [
    #                 "Understand variables",
    #                 "Write basic functions"
    #             ]
    #         },
    #         {
    #             "tag": "B",
    #             "outcome": "Advanced Python",
    #             "sub_items": [
    #                 "Master classes and objects",
    #                 "Work with modules"
    #             ]
    #         }
    #     ]
    #
    #     outcomes = self.llm.extract_learning_outcomes(generated_text)
    #
    #     # Print the output to observe the result
    #     print("Extracted Learning Outcomes:", outcomes)
    #
    #     # Assertions to check if outcomes are extracted correctly
    #     self.assertEqual(outcomes, expected_outcomes)
    #
    # def test_extract_content_listing(self):
    #     generated_text = """
    #     Module 1: Introduction to Python
    #       - Content Item 1.1: Python Installation
    #         Type: Video
    #         Duration: 10
    #       - Content Item 1.2: Python Basics
    #         Type: Reading
    #     Module 2: Advanced Python
    #       - Content Item 2.1: Classes and Objects
    #         Type: Reading
    #     """
    #     expected_listing = [
    #         {
    #             "module_number": "1",
    #             "module_title": "Introduction to Python",
    #             "contents": [
    #                 {"item_number": "1.1", "item_title": "Python Installation"},
    #                 {"item_number": "1.2", "item_title": "Python Basics"}
    #             ]
    #         },
    #         {
    #             "module_number": "2",
    #             "module_title": "Advanced Python",
    #             "contents": [
    #                 {"item_number": "2.1", "item_title": "Classes and Objects"}
    #             ]
    #         }
    #     ]
    #
    #     content_listing = self.llm.extract_content_listing(generated_text)
    #
    #     # Print the output to observe the result
    #     print("Extracted Content Listing:", content_listing)
    #
    #     # Assertions to check if content listing is extracted correctly
    #     self.assertEqual(content_listing, expected_listing)
    #
    # def test_generate_summary(self):
    #     text_chunk = "Python is a versatile programming language used for web development, data analysis, and more."
    #
    #     # Call the actual generate_summary method
    #     summary = self.llm.generate_summary(text_chunk)
    #
    #     # Print the output to observe the result
    #     print("Generated Summary:", summary)
    #
    #     # Basic assertion to check if summary is not empty
    #     self.assertTrue(len(summary) > 0, "Summary should not be empty.")
    #
    # def test_generate_response(self):
    #     prompt = "Summarize the following text."
    #
    #     # Call the actual generate_response method
    #     response = self.llm.generate_response(prompt)
    #
    #     # Print the output to observe the result
    #     print("Generated Response:", response)
    #
    #     # Basic assertion to check if response is not empty
    #     self.assertTrue(len(response) > 0, "Response should not be empty.")
    #
