import requests
import ollama
import re

def generate_course_title_and_description(step1_data):
    """
    Generates a course title and description based on Step 1 data using LLM3 of Ollama.
    """
    # Define the prompt based on Step 1 data
    prompt = f"""
    Given the following course information, generate a course title and a detailed description:
    Course Type: {step1_data.get('course_type', 'General')}
    Prerequisite Knowledge: {step1_data.get('prerequisite_knowledge', 'None')}
    Participants Info: {step1_data.get('participants_info', 'General')}
    Available Material: {step1_data.get('available_material', 'None')}
    Duration: {step1_data.get('duration', 'Undefined')}
    Knowledge Level: {step1_data.get('knowledge_level', 'Beginner')}

    Output should be in the following format:
    Title: <Course Title>
    Description: <Course Description>
    """
    print("prompt \n" + str(prompt))

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
        print(f"Error communicating with Ollama API: {e}")
        return "", ""


# course_maker/ollama_helper.py

def generate_learning_outcomes(course_title, course_description):
    """
    Generates learning outcomes and sub-items based on course title and description using LLM3 of Ollama.
    """
    # Define the prompt based on the course title and description
    prompt = f"""
    You are a course designer. Based on the given course title and description, generate several learning outcomes.
    Tag each learning outcome with a unique letter starting from 'A', and for each outcome, provide sub-items.
    Ensure the learning outcomes are practical, understandable, and related to the course content.

    Course Title: {course_title}
    Course Description: {course_description}

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
    print("prompt \n" + str(prompt))

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

        print("-------------------")
        print(simplified_outcomes)
        return simplified_outcomes

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return []

def generate_content_listing(course_title, course_description):
    """
    Generates a structured content listing based on course title and description using LLM3 of Ollama.
    The content is categorized into modules, which include items and sub-items.
    """
    # Define the prompt based on the course title and description
    prompt = f"""
    You are a course content developer. Based on the given course title and description, generate a detailed content structure.
    The content should be organized into modules, with each module containing items and sub-items.
    Each content item should be one of the following types: Note, Quiz, Reading, Video.
    Tag the content items appropriately and make sure to use a logical hierarchy.

    Course Title: {course_title}
    Course Description: {course_description}

    Provide the content in the following format:
    Module 1: [Module Title]
      - Item 1.1: [Title] (Type: [Type: Note/Quiz/Reading/Video])
        - Sub-item 1.1.1: [Title]
        - Sub-item 1.1.2: [Title]
      - Item 1.2: [Title] (Type: [Type: Note/Quiz/Reading/Video])
    Module 2: [Module Title]
      - Item 2.1: [Title] (Type: [Type: Note/Quiz/Reading/Video])

    Only return the list of modules, items, and sub-items in this structured format.
    """
    print("prompt \n" + str(prompt))

    try:
        # Generate response using Ollama locally
        response = ollama.generate(model='llama3', prompt=prompt)

        # Extract the generated text from the response dictionary
        generated_text = response.get('response', "")

        # Extract content listing using regex
        content_listing = []
        current_module = None

        module_pattern = r"Module (\d+):\s*(.+)"
        item_pattern = r"- Item (\d+\.\d+):\s*(.+)\s+\(Type:\s*(.+)\)"
        sub_item_pattern = r"- Sub-item (\d+\.\d+\.\d+):\s*(.+)"

        for line in generated_text.splitlines():
            module_match = re.match(module_pattern, line.strip())
            item_match = re.match(item_pattern, line.strip())
            sub_item_match = re.match(sub_item_pattern, line.strip())

            if module_match:
                # New module
                module_number = module_match.group(1)
                module_title = module_match.group(2)
                current_module = {
                    "module_number": module_number,
                    "module_title": module_title,
                    "items": []
                }
                content_listing.append(current_module)

            elif item_match and current_module:
                # New item within the current module
                item_number = item_match.group(1)
                item_title = item_match.group(2)
                item_type = item_match.group(3)
                current_item = {
                    "item_number": item_number,
                    "item_title": item_title,
                    "item_type": item_type,
                    "sub_items": []
                }
                current_module["items"].append(current_item)

            elif sub_item_match and current_module:
                # Sub-item for the current item
                sub_item_number = sub_item_match.group(1)
                sub_item_title = sub_item_match.group(2)
                if current_module["items"]:
                    current_module["items"][-1]["sub_items"].append({
                        "sub_item_number": sub_item_number,
                        "sub_item_title": sub_item_title
                    })
        print("Ollama Response for generate_content_listing")
        print(generated_text)
        return generated_text

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return []