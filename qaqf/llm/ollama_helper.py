# ollama_helper.py

import requests
import ollama
import re
from course_maker.utils.pdf_utils import read_pdf
from .models import Courses, Log
from django.utils import timezone
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def log_to_db(function_name, course_id, input_data, output_data=None, error_message=None):
    Log.objects.create(
        function_name=function_name,
        course_id=course_id,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message,
        timestamp=timezone.now()
    )

def generate_course_title_and_description(course_id):
    """
    Generates a course title and description based on Step 1 data using LLM3 of Ollama.
    """
    course = Courses.objects.get(pk=course_id)
    prompt = f"""
        Given the following course information, generate a course title and a detailed description:
        About Course: {course.course_description}
        Course Type: {course.course_type}
        Previous educational level: {course.prerequisite_knowledge}
        Learners Details: {course.participants_info}
        Ensure the generated title and description are correct and relevant.
    """

    try:
        log_to_db("generate_course_title_and_description", course_id, prompt)

        response = ollama.generate(model='llama3', prompt=prompt)
        generated_text = response.get('response', "")

        title_match = re.search(r"Title:\s*(.+)", generated_text)
        description_match = re.search(r"Description:\s*(.+)", generated_text)

        title = title_match.group(1).strip() if title_match else ""
        description = description_match.group(1).strip() if description_match else ""

        log_to_db("generate_course_title_and_description", course_id, prompt, f"Title: {title}, Description: {description}")

        return title, description

    except requests.exceptions.RequestException as e:
        log_to_db("generate_course_title_and_description", course_id, prompt, error_message=str(e))
        return "", ""

def generate_learning_outcomes(course_id):
    """
    Generates learning outcomes and sub-items based on course title and description using LLM3 of Ollama.
    """
    course = Courses.objects.get(pk=course_id)
    prompt = f"""
        Based on the course title '{course.course_title}' and description '{course.course_description}', 
        generate learning outcomes tagged with letters starting from 'A', each with sub-items (e.g., A1, A2).
    """
    try:
        log_to_db("generate_learning_outcomes", course_id, prompt)

        response = ollama.generate(model='llama3', prompt=prompt)
        generated_text = response.get('response', "")

        # Regex to extract outcomes and sub-items
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
                sub_item_text = sub_item_match.group(2)
                current_outcome["sub_items"].append(sub_item_text)

        log_to_db("generate_learning_outcomes", course_id, prompt, str(learning_outcomes))
        return learning_outcomes

    except requests.exceptions.RequestException as e:
        log_to_db("generate_learning_outcomes", course_id, prompt, error_message=str(e))
        return []

def generate_content_listing(course_id):
    """
    Generates a structured content listing based on the course title and description using LLM3 of Ollama.
    """
    course = Courses.objects.get(pk=course_id)
    prompt = f"""
        Based on the course title '{course.course_title}' and description '{course.course_description}', 
        generate a structured content listing organized into modules.
    """
    try:
        log_to_db("generate_content_listing", course_id, prompt)

        response = ollama.generate(model='llama3', prompt=prompt)
        generated_text = response.get('response', "")

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

        log_to_db("generate_content_listing", course_id, prompt, str(content_listing))
        return content_listing

    except requests.exceptions.RequestException as e:
        log_to_db("generate_content_listing", course_id, prompt, error_message=str(e))
        return []

def generate_summary(text_chunk):
    """
    Generates a summary of a chunk of text using Ollama.
    """
    prompt = f"Summarize the key points of the following text: {text_chunk}"
    try:
        response = ollama.generate(model='llama3', prompt=prompt)
        return response.get('response', "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error summarizing: {e}")
        return ""

def create_chunks(text, chunk_size=1000):
    """
    Splits a long text into smaller chunks of a specified size.
    """
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks
