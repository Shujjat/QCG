# LLM Implementation.py
from django.conf import settings
from datetime import datetime
import requests
import ollama
import re
import time
from course_maker.models import Courses, LearningOutcome
from course_maker.utils.pdf_utils import read_pdf
from .models import LoggingEntry
from .PromptBuilder import PromptBuilder
from .utils import *
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class LLM:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.prompt_builder = PromptBuilder()

        self.llm_list = self.list_ollama_models()

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
    def generate_course_title_and_description(self,course_id,item_type=None):
        """
        Generates a course title and description based on Step 1 data using LLM3 of Ollama.
        """
        # Define the prompt based on Step 1 data

        # Retrieve the course using course_id
        course = Courses.objects.get(pk=course_id)

        if course.available_material:

            pdf_path = f"{settings.BASE_URL}{course.available_material.url}"
            pdf = read_pdf(pdf_path)
            chunks = self.create_chunks(pdf, chunk_size=len(pdf))  # Split into chunks of 500 words
            available_material = "\n".join([self.generate_summary(chunk) for chunk in chunks])
            course.available_material_content = available_material
            course.save()


        # Define task description and output format
        task_description = "generate a course title and a detailed description"
        output_format = """
               Title: <Course Title>
               Description: <Course Description>
               """

        # Build the full prompt using the PromptBuilder
        prompt = self.prompt_builder.build_full_prompt(task_description, course, output_format,item_type)

        logger.info(prompt)

        try:
            generated_text = self.generate_response(prompt=prompt)
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

    @log_execution
    def generate_learning_outcomes(self,course_id,item_id=None):
        """
        Generates learning outcomes and sub-items based on course title and description using LLM3 of Ollama.
        """
        course = Courses.objects.get(pk=course_id)


        # Define the prompt based on the course title and description

        task_description = """
                            Based on the given course title: '{course.course_title}' 
                            and description: '{course.course_description}', generate several learning outcomes 
                            that should a learner achieve.
        """
        output_format = """
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

        prompt = self.prompt_builder.build_full_prompt(task_description, course, output_format,'learning_outcome', item_id)
        logger.info(prompt)
        try:
            # Generate response using Ollama locally
            generated_text = self.generate_response( prompt=prompt)
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

    @log_execution
    def generate_content_listing(self,course_id,item_id=None):
        """
        Generates a structured content listing based on course title and description using LLM3 of Ollama.
        The content is categorized into modules, which include items and sub-items.
        The structure is adjusted to fit the ContentListing and Content models.
        """

        # Define the prompt based on the course title and description
        course = Courses.objects.get(pk=course_id)


        task_description = """
                                    Based on the given course title: '{course.course_title}' 
                                    and description: '{course.course_description}',  
                            """
        output_format="""
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
        prompt = self.prompt_builder.build_full_prompt(task_description, course, output_format,'content_listing', item_id)
        logger.info(prompt)
        try:
            # Generate response using Ollama locally
            generated_text = self.generate_response( prompt=prompt)
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


            return generated_text

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama API: {e}")
            return []
    @log_execution
    def generate_summary(self,text_chunk):
        prompt = f"""
        Summarize the key points of the following book excerpt concisely and informatively:
            {text_chunk}
        """
        response = ollama.generate(model='llama3', prompt=prompt)
        return response.get('response', "")
    @log_execution
    def create_chunks(self,text, chunk_size=1000):
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
        if get_ollama_status():
            run_ollama_package()
        if not model:
            model=settings.DEFAULT_LLM

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
            model = getattr(settings, 'OLLAMA_DEFAULT_MODEL', 'llama3.2')  # Default to 'llama3.2' if not set in settings
        logger.info("Model: " + model)

        try:
            response = ollama.generate(model=model, prompt=prompt)
            #Shutting down Ollama to secure system resources
            shutdown_ollama()
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

    def list_ollama_models(self):
        """Check if Ollama is running, and list all models"""
        if not get_ollama_status():
            run_ollama_package()

        try:
            # Run the command to list models and capture output
            result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Parse the output (assuming it's in JSON format)
            models = json.loads(result.stdout)
            return [model['name'] for model in models]
        except Exception as e:
            print(f"Error fetching models from Ollama: {e}")
            return []