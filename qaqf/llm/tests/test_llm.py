import subprocess
import requests
from datetime import datetime
from django.conf import settings
from rest_framework.test import APITestCase
from course_maker.models import Courses
from llm.llm import LLM
from llm.models import LoggingEntry
from django.core.files import File

class TestLLM(APITestCase):

    @classmethod
    def setUpTestData(cls):

        # Initialize LLM instance once for all tests
        cls.llm = LLM()

    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        # Create an in-memory PDF file
        pdf_path = f"{settings.BASE_DIR}/media/sample_books/python.pdf"
        # Set up test course
        with open(pdf_path, 'rb') as pdf_file:
            self.course = Courses.objects.create(
                course_title="",
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
                available_material=File(pdf_file, name='python.pdf')  # Add the file here
            )

    def test_generate_course_title(self):
        # Call the method directly with actual course ID
        title, _ = self.llm.generate_course_title_and_description(self.course.id)

        # Assertions
        self.assertTrue(title, "Title should not be empty")

    def test_generate_course_description(self):
        # Call the method directly with actual course ID
        _, description = self.llm.generate_course_title_and_description(self.course.id)

        # Assertions

        self.assertTrue(description, "Description should not be empty")

    def test_generate_learning_outcomes(self):
        self.llm.generate_course_title_and_description(self.course.id)
        outcomes = self.llm.generate_learning_outcomes(self.course.id)

        # Assertions
        self.assertTrue (outcomes, "Learning outcomes should not be empty")
        self.assertTrue( isinstance(outcomes, list), "Outcomes should be a list")
        self.assertTrue( all("outcome" in outcome for outcome in outcomes), "Each outcome should have a 'outcome' field")

    def test_generate_content_listing(self):
        self.llm.generate_course_title_and_description(self.course.id)
        self.llm.generate_learning_outcomes(self.course.id)
        content_listing = self.llm.generate_content_listing(self.course.id)

        # Assertions
        self.assertTrue (content_listing, "Content listing should not be empty")
        self.assertTrue (isinstance(content_listing, list), "Content listing should be a list")
        self.assertTrue (all(
            "module_title" in module for module in content_listing), "Each module should have a 'module_title' field")

    def test_extract_learning_outcomes(self):
        generated_text = """
        - Outcome A: Understand the basics
            - A1: Definition of basics
            - A2: Examples of basics
        - Outcome B: Apply knowledge in practice
            - B1: Practical application 1
            - B2: Practical application 2
        """

        learning_outcomes = self.llm.extract_learning_outcomes(generated_text)

        # Assertions
        assert learning_outcomes, "Learning outcomes should not be empty"
        assert all("outcome" in outcome for outcome in learning_outcomes), "Each outcome should have an 'outcome' field"





    def test_generate_summary(self):
        text_chunk = self.course.available_material_content
        summary = self.llm.generate_summary(text_chunk)

        # Assertions
        self.assertTrue( summary, "Summary should not be empty")
        self.assertTrue( isinstance(summary, str), "Summary should be a string")

    def test_create_chunks(self):
        text = " ".join(["word"] * 3000)  # Simulating a text with 3000 words
        chunk_size = 1000

        chunks = self.llm.create_chunks(text, chunk_size=chunk_size)

        # Assertions
        self.assertTrue( len(chunks) > 1, "Text should be split into multiple chunks")
        self.assertTrue( all(len(chunk.split()) <= chunk_size for chunk in
                   chunks), "Each chunk should be within the specified chunk size")

    def test_log_to_db(self):
        # Call method to log start, end, and duration in database
        start_time = datetime.now()
        self.llm.log_to_db("test_log_to_db", start_time=start_time, status="Completed")

        # Assertions
        log_entry = LoggingEntry.objects.filter(function_name="test_log_to_db").first()
        assert log_entry is not None, "Log entry should be created"
        assert log_entry.status == "Completed", "Status should be 'Completed'"

    def test_generate_response(self):
        # Test prompt and model name
        prompt = "Summarize the following text: 'Python is a programming language.'"

        response = self.llm.generate_response(prompt=prompt, model=settings.DEFAULT_LLM)

        # Assertions
        assert response, "Response should not be empty"
        assert isinstance(response, str), "Response should be a string"


    def test_extract_content_listing(self):
        generated_text = """
        Module 1: Introduction to Python
            - Content Item 1.1: Basics of Python
            - Content Item 1.2: Python Syntax
        Module 2: Advanced Topics
            - Content Item 2.1: Data Structures
            - Content Item 2.2: Algorithms
        """

        content_listing = self.llm.extract_content_listing(generated_text)

        # Assertions
        self.assertTrue( content_listing, "Content listing should not be empty")
        self.assertTrue( all(
            "module_title" in module for module in content_listing),
            "Each module should have a 'module_title' field")

    def _test_list_ollama_models(self):
        # Test for Ollama model listing
        models = self.llm.list_ollama_models()

        # Assertions
        self.assertTrue( isinstance(models, list), "Models should be a list")
        self.assertTrue( models, "Models list should not be empty")



def check_django_status(url='http://localhost:8000/'):
    try:
        # Try sending a request to the Django app
        response = requests.get(url, timeout=5)  # Timeout set to 5 seconds
        # If the status code is 200, Django is running
        if response.status_code == 200:
            print(f"Django is running at {url}")
            return True
        else:
            print(f"Received unexpected status code {response.status_code} from {url}")
            return False
    except requests.ConnectionError:
        print(f"Failed to connect to {url}")
        return False
    except requests.Timeout:
        print(f"Request to {url} timed out")
        return False


def run_django_server():
    # Command to start Django's development server
    command = ["python", "manage.py", "runserver"]

    try:
        # Use subprocess to run the command in a non-blocking way
        subprocess.Popen(command)
        print("Django development server is now running.")
    except Exception as e:
        print(f"Error starting the Django server: {e}")
