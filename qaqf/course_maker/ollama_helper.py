import requests
import ollama
import re
import sys
from .utils.pdf_utils import read_pdf
from .models import Courses
import logging
logging.basicConfig(level=logging.WARNING)
from django.conf import settings
logger = logging.getLogger(__name__)



def generate_course_title_and_description(course_id):
    """
    Generates a course title and description based on Step 1 data using LLM3 of Ollama.
    """
    # Define the prompt based on Step 1 data

    # Retrieve the course using course_id
    course = Courses.objects.get(pk=course_id)

    # Check if the available material is a valid file (assuming it's a FileField)
    prompt = f"""
                    Given the following course information, generate a course title and a detailed description:
                    About Course: {course.course_description}
                    Course Type: {course.course_type}
                    Previous educational level: {course.prerequisite_knowledge}
                    Learners Details: {course.participants_info}
                    There is extensive study material available for this course. Please use it as needed to generate a relevant and coherent response:

                    
                    """
    if course.available_material:
        pdf_path = f"{settings.BASE_URL}{course.available_material.url}"
        pdf= read_pdf(pdf_path)
        chunks = create_chunks(pdf, chunk_size=len(pdf))  # Split into chunks of 500 words
        available_material = "\n".join([generate_summary(chunk) for chunk in chunks])
        course.available_material_content=available_material
        course.save()
        prompt += f"""
            
            [Available Study Material: Start]
            {available_material}
            [Available Study Material: End]
               
                """




    prompt+=""" Duration of Course: {course.duration}
            Target Knowledge Level to achieve: {course.knowledge_level}
            Ensure the generated title and description is correct and relevant. 

            Also, output should be in the following format:
            Title: <Course Title>
            Description: <Course Description>"""

    try:
        response = ollama.generate(model='llama3', prompt=prompt)

        # Extract the generated text from the response dictionary
        generated_text = response.get('response', "")
        title, description = "", ""

        # Use regex to extract the title and description
        title_match = re.search(r"Title:\s*(.+)", generated_text)
        description_match = re.search(r"Description:\s*(.+)", generated_text)

        if title_match:
            title = title_match.group(1).strip()

        if description_match:
            description = description_match.group(1).strip()

        return title, description
    except requests.exceptions.RequestException as e:
        return "", ""


# course_maker/ollama_helper.py

def generate_learning_outcomes(course_id):
    """
    Generates learning outcomes and sub-items based on course title and description using LLM3 of Ollama.
    """
    course = Courses.objects.get(pk=course_id)
    # Define the prompt based on the course title and description
    prompt = f"""
    You are a course designer. Based on the given course title: '{course.course_title}' 
    and description: '{course.course_description}', generate several learning outcomes 
    that should a learner achieve.
    
    There is extensive study material available for this course. Please use it as 
    needed to generate a relevant and coherent learning outcomes:

    [Available Study Material: Start]
    {course.available_material_content}
    [Available Study Material: End]
    Ensure the learning outcomes are practical, understandable, and related to the Available Study Material.
    
    Tag each learning outcome with a unique letter starting from 'A', and for each outcome, provide sub-items.
    

    Please provide the outcomes in the following format:
    - Outcome A: [Main learning outcome for A]
        - A1: [First sub-item for A]
        - A2: [Second sub-item for A]
    - Outcome B: [Main learning outcome for B]
        - B1: [First sub-item for B]
        - B2: [Second sub-item for B]
    and so on

    Only return the list of learning outcomes with tags and sub-items.
    """
    logger.info("Prompt")

    logger.info( str(prompt))

    try:
        # Generate response using Ollama locally
        response = ollama.generate(model='llama3', prompt=prompt)

        # Extract the generated text from the response dictionary
        generated_text = response.get('response', "")

        # Extract outcomes and sub-items using regex
        learning_outcomes = []
        current_outcome = None

        outcome_pattern = r"- Outcome ([A-Z]):\s*(.+)"
        sub_item_pattern = r"- ([A-Z]\d+):\s*(.+)"

        for line in generated_text.splitlines():
            outcome_match = re.match(outcome_pattern, line.strip())
            sub_item_match = re.match(sub_item_pattern, line.strip())

            if outcome_match:
                # New learning outcome
                tag = outcome_match.group(1)
                outcome_text = outcome_match.group(2)
                current_outcome = {
                    "tag": tag,
                    "number": 1,
                    "outcome": outcome_text,
                    "sub_items": []
                }
                learning_outcomes.append(current_outcome)

            elif sub_item_match and current_outcome:
                # Sub-item for the current learning outcome
                sub_item_tag = sub_item_match.group(1)
                sub_item_text = sub_item_match.group(2)
                current_outcome["sub_items"].append(sub_item_text)

        # Create a simplified structure for the learning outcomes
        simplified_outcomes = []
        for outcome in learning_outcomes:
            simplified_outcomes.append({
                "tag": outcome["tag"],
                "number": outcome["number"],
                "outcome": outcome["outcome"],
                "sub_items": outcome["sub_items"]
            })


        return simplified_outcomes

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama API: {e}")
        return []


def generate_content_listing(course_id):
    """
    Generates a structured content listing based on course title and description using LLM3 of Ollama.
    The content is categorized into modules, which include items and sub-items.
    The structure is adjusted to fit the ContentListing and Content models.
    """

    # Define the prompt based on the course title and description
    course = Courses.objects.get(pk=course_id)

    prompt = f"""
    You are a course content developer. Based on the given course title:'{course.course_title}'
    and description:'{course.course_description}', 
    and study material:
    [Available Study Material: Start]
    {course.available_material_content}
    [Available Study Material: End]
    
    generate a detailed content structure.
    The content should be organized into modules, with each module containing content items.
    Each content item should contain the following attributes: Content Item, Type, Duration, Key Points,
    and Script.

    - Content Item: This is the title of the content item.
    - Type: It should be either 'Video' or 'Reading'.
    - Duration: Duration in minutes for videos, optional for readings.
    - Key Points: Highlight important takeaways for each content item.
    - Script: Provide a brief script, if applicable.

    Provide the content in the following structured format:

    Module 1: [Module Title]
      - Content Item 1.1: [Title]
        Type: [Video/Reading]
        Duration: [Duration in minutes, if applicable]
        Key Points: [List key points, if any]
        Script: [Provide a script, if any]

      - Content Item 1.2: [Title]
        Type: [Video/Reading]
        Duration: [Duration in minutes, if applicable]
        Key Points: [List key points, if any]
        Script: [Provide a script, if any]

    Module 2: [Module Title]
      - Content Item 2.1: [Title]
        Type: [Video/Reading]
        Duration: [Duration in minutes, if applicable]
        Key Points: [List key points, if any]
        Script: [Provide a script, if any]

    Only return the list of modules, items, and their attributes in this structured format.
    """
    logger.info("prompt \n" + str(prompt))


    try:
        # Generate response using Ollama locally
        response = ollama.generate(model='llama3', prompt=prompt)

        # Extract the generated text from the response dictionary
        generated_text = response.get('response', "")

        # Extract content listing using regex
        content_listing = []
        current_module = None

        module_pattern = r"Module (\d+):\s*(.+)"
        content_item_pattern = r"- Content Item (\d+\.\d+):\s*(.+)"
        type_pattern = r"Type:\s*(.+)"
        duration_pattern = r"Duration:\s*(\d+)"
        key_points_pattern = r"Key Points:\s*\[(.*?)\]"
        script_pattern = r"Script:\s*(.+)"

        for line in generated_text.splitlines():
            module_match = re.match(module_pattern, line.strip())
            content_item_match = re.match(content_item_pattern, line.strip())
            type_match = re.match(type_pattern, line.strip())
            duration_match = re.match(duration_pattern, line.strip())
            key_points_match = re.match(key_points_pattern, line.strip())
            script_match = re.match(script_pattern, line.strip())

            if module_match:
                # New module
                module_number = module_match.group(1)
                module_title = module_match.group(2)
                current_module = {
                    "module_number": module_number,
                    "module_title": module_title,
                    "contents": []
                }
                content_listing.append(current_module)

            elif content_item_match and current_module:
                # New content item within the current module
                item_number = content_item_match.group(1)
                item_title = content_item_match.group(2)
                current_content = {
                    "item_number": item_number,
                    "item_title": item_title,
                    "type": "",
                    "duration": None,
                    "key_points": "",
                    "script": ""
                }
                current_module["contents"].append(current_content)

            elif type_match and current_module and current_module["contents"]:
                current_module["contents"][-1]["type"] = type_match.group(1)

            elif duration_match and current_module and current_module["contents"]:
                current_module["contents"][-1]["duration"] = int(duration_match.group(1))

            elif key_points_match and current_module and current_module["contents"]:
                current_module["contents"][-1]["key_points"] = key_points_match.group(1)

            elif script_match and current_module and current_module["contents"]:
                current_module["contents"][-1]["script"] = script_match.group(1)

        logger.info("=====================generated_text==================")
        logger.info(generated_text)
        return generated_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama API: {e}")
        return []
def generate_summary(text_chunk):
    prompt = f"""
    Summarize the key points of the following book excerpt concisely and informatively:
        {text_chunk}
    """
    response = ollama.generate(model='llama3', prompt=prompt)
    return response.get('response', "")

def create_chunks(text, chunk_size=1000):
    """
    Splits a long text into chunks of a specific size.

    Parameters:
    text (str): The text to be split.
    chunk_size (int): The number of words per chunk.

    Returns:
    list: A list of text chunks.
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunks.append(' '.join(words[i:i + chunk_size]))

    return chunks

