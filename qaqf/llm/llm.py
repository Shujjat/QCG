# LLM Implementation.py
import json
import sys

from django.conf import settings
from datetime import datetime
import requests
import ollama
import re
import time
from course_maker.models import Courses
from course_maker.utils.pdf_utils import read_pdf
from .models import LoggingEntry
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class LLM:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    # Utility function for logging to DB
    def log_to_db(self, function_name, start_time, end_time=None, status='Started'):
        # Check if start_time or end_time is None
        if start_time is None or end_time is None:
            print("Error: start_time or end_time is None")
            return

        # If start_time and end_time are floats (representing timestamps), convert them to datetime
        if isinstance(start_time, float):
            start_time = datetime.fromtimestamp(start_time)
        if isinstance(end_time, float):
            end_time = datetime.fromtimestamp(end_time)

        # Check if both are now datetime objects, and calculate duration
        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            duration = (end_time - start_time).total_seconds()
            print(f"Duration: {duration} seconds")
            # Log the duration and additional info to the database
        else:
            print("Error: start_time and end_time must be valid datetime objects or timestamps.")

        log_entry = LoggingEntry(
                function_name=function_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status=status
            )
        log_entry.save()

    # Decorator to log start, end, and duration
    def log_execution(func):
        def wrapper(self, *args, **kwargs):  # Add 'self' to handle class methods
            function_name = func.__name__
            start_time = time.time()

            # Log start of the function
            logger.info(f"Starting {function_name}")
            self.log_to_db(function_name=function_name, start_time=start_time, status='Started')

            try:
                # Call the function
                result = func(self, *args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time

                # Log successful completion
                logger.info(f"Completed {function_name} in {duration} seconds")
                self.log_to_db(function_name=function_name, start_time=start_time, end_time=end_time, status='Completed')

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                # Log error and failure
                logger.error(f"Error in {function_name}: {str(e)}")
                self.log_to_db(function_name=function_name, start_time=start_time, end_time=end_time, status='Failed')
                raise e

            return result

        return wrapper

    @log_execution
    def generate_course_title_and_description(self, course_id):
        """
        Generates a course title and description based on Step 1 data using LLM3 of Ollama.
        """
        course = Courses.objects.get(pk=course_id)

        # Constructing the prompt
        prompt = f"""
            Given the following course information, generate a course title and a detailed description:
            About Course: {course.course_description}
            Course Type: {course.course_type}
            Previous educational level: {course.prerequisite_knowledge}
            Learners Details: {course.participants_info}
        """

        if course.available_material:
            pdf_path = 'http://127.0.0.1:8000' + str(course.available_material.url)
            pdf = read_pdf(pdf_path)
            chunks = self.create_chunks(pdf, chunk_size=len(pdf))
            available_material = "\n".join([self.generate_summary(chunk) for chunk in chunks])
            course.available_material_content = available_material
            course.save()
            prompt += f"""
                [Available Study Material: Start]
                {available_material}
                [Available Study Material: End]
            """

        prompt += f"""
            Duration of Course: {course.duration}
            Target Knowledge Level to achieve: {course.knowledge_level}
            Ensure the generated title and description are correct and relevant.
            Output format:
            Title: <Course Title>
            Description: <Course Description>
        """
        logger.info(prompt)
        try:
            generated_text  = self.generate_response(prompt,None)

            title, description = "", ""

            # Extract the title and description using regex
            title_match = re.search(r"Title:\s*(.+)", generated_text)
            description_match = re.search(r"Description:\s*(.+)", generated_text)

            if title_match:
                title = title_match.group(1).strip()
            if description_match:
                description = description_match.group(1).strip()

            return title, description
        except requests.exceptions.RequestException as e:
            return "", ""

    @log_execution
    def generate_learning_outcomes(self, course_id):
        """
        Generates learning outcomes based on the course title and description using LLM3 of Ollama.
        """
        course = Courses.objects.get(pk=course_id)

        prompt = f"""
            You are a course designer. Based on the given course title: '{course.course_title}' 
            and description: '{course.course_description}', generate several learning outcomes 
            that a learner should achieve.
        """

        if course.available_material_content:
            prompt += f"""
                There is extensive study material available for this course. Please use it as needed:
                [Available Study Material: Start]
                {course.available_material_content}
                [Available Study Material: End]
            """

        prompt += """
            Ensure the learning outcomes are practical, understandable, and related to the study material.
            Format:
            - Outcome A: [Main learning outcome]
                - A1: [First sub-item]
                - A2: [Second sub-item]
            - Outcome B: [Main learning outcome]
                - B1: [First sub-item]
                - B2: [Second sub-item]
        """
        logger.info(prompt)
        try:

            logger.info(prompt)
            # Parse the learning outcomes and sub-items
            learning_outcomes = self.extract_learning_outcomes(self.generate_response(prompt,None))

            return learning_outcomes
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama API: {e}")
            return []

    @log_execution
    def generate_content_listing(self, course_id):
        """
        Generates a structured content listing based on course title and description using LLM3 of Ollama.
        """
        course = Courses.objects.get(pk=course_id)

        prompt = f"""
            Based on the given course title: '{course.course_title}' and description: '{course.course_description}', 
            generate a content structure organized into modules. Each module contains content items:
            [Available Study Material: Start]
            {course.available_material_content}
            [Available Study Material: End]
        """

        try:
            response = self.generate_response(prompt)
            generated_text = response.get('response', "")

            # Extract content listing from generated text
            content_listing = self.extract_content_listing(generated_text)

            return content_listing
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama API: {e}")
            return []
    @log_execution

    def generate_summary(self, text_chunk):
        prompt = f"""
            Summarize the key points of the following book excerpt concisely and informatively:
                {text_chunk}
        """
        response = ollama.generate(model='llama3', prompt=prompt)
        return response.get('response', "")
    @log_execution

    def create_chunks(self, text, chunk_size=1000):
        """
        Splits a long text into chunks of a specific size.
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunks.append(' '.join(words[i:i + chunk_size]))

        return chunks
    @log_execution

    def extract_learning_outcomes(self, generated_text):
        """
        Extract learning outcomes and sub-items from generated text using regex.
        """
        learning_outcomes = []
        outcome_pattern = r"- Outcome ([A-Z]):\s*(.+)"
        sub_item_pattern = r"- ([A-Z]\d+):\s*(.+)"

        current_outcome = None

        for line in generated_text.splitlines():
            outcome_match = re.match(outcome_pattern, line.strip())
            sub_item_match = re.match(sub_item_pattern, line.strip())

            if outcome_match:
                tag = outcome_match.group(1)
                outcome_text = outcome_match.group(2)
                current_outcome = {"tag": tag, "outcome": outcome_text, "sub_items": []}
                learning_outcomes.append(current_outcome)
            elif sub_item_match and current_outcome:
                current_outcome["sub_items"].append(sub_item_match.group(2))

        return learning_outcomes
    @log_execution

    def extract_content_listing(self, generated_text):
        """
        Extract content listing with modules and items from generated text using regex.
        """
        content_listing = []
        module_pattern = r"Module (\d+):\s*(.+)"
        content_item_pattern = r"- Content Item (\d+\.\d+):\s*(.+)"

        current_module = None

        for line in generated_text.splitlines():
            module_match = re.match(module_pattern, line.strip())
            content_item_match = re.match(content_item_pattern, line.strip())

            if module_match:
                module_number = module_match.group(1)
                module_title = module_match.group(2)
                current_module = {"module_number": module_number, "module_title": module_title, "contents": []}
                content_listing.append(current_module)
            elif content_item_match and current_module:
                item_number = content_item_match.group(1)
                item_title = content_item_match.group(2)
                current_module["contents"].append({"item_number": item_number, "item_title": item_title})

        return content_listing


    def generate_response(self,prompt, model=None):
        """
        Generate a response using the Ollama API, selecting the model dynamically from settings.

        Args:
            prompt (str): The input prompt for the Ollama API.
            model (str): The model to use for generation. If None, the default model from settings will be used.

        Returns:
            dict: The response from the Ollama API.
        """
        # Fetch the model from settings if not provided
        logger.info("Generating response")
        if not model:
            model = getattr(settings, 'OLLAMA_DEFAULT_MODEL', 'llama3')  # Default to 'llama3' if not set in settings
        logger.info("Model: " + model)

        try:
            response = ollama.generate(model=model, prompt=prompt)

            # Check if the response object has a JSON serializable structure
            if isinstance(response, dict):
                # It's already a dictionary, so it should be serializable
                logger.info("Response is already a dict")
            else:
                # Try converting to a dict if it's an object
                try:
                    response = response.__dict__
                    logger.info("Converted response to dict using __dict__")
                except AttributeError:
                    logger.error("Response object has no __dict__ attribute")

            # Attempt to serialize it to JSON to check if it's valid
            try:
                json_response = json.dumps(response)
                logger.info("Successfully serialized response to JSON")
                logger.info(json_response)
            except TypeError as e:
                logger.error(f"Error serializing response: {e}")
                raise

            # Return the 'response' part from the generated response
            return response.get('response', "")

        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return ""
