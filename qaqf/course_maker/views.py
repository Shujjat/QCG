# course_maker/views.py
import json
from sys import platform
import re

from rest_framework.views import APIView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from .course_wizard_forms import *
from rest_framework import generics, viewsets
from rest_framework.response import Response
from .models import Courses, LearningOutcome,Content,ContentListing
from .serializers import CourseSerializer, LearningOutcomeSerializer, ContentSerializer, ContentListingSerializer
from llm import llm
from rest_framework import status
from django.http import JsonResponse
import subprocess
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
llm_instance=llm.LLM()
# Define the forms for each step
FORMS = [
    ("step1", Step1Form),
    ("step2", Step2Form),
    ("step3", Step3Form),
    ("step4", Step4Form),
    ("step5", Step5Form),
    ("step6", Step6Form),
]

# Templates for each step
TEMPLATES = {
    "step1": "course_maker/step1.html",
    "step2": "course_maker/step2.html",
    "step3": "course_maker/step3.html",
    "step4": "course_maker/step4.html",
    "step5": "course_maker/step5.html",
    "step6": "course_maker/step6.html",
}

# File storage settings
file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)


# Wizard view for course creation
class CourseCreationWizard(SessionWizardView):
    template_name = "course_maker/form_wizard.html"
    form_list = FORMS
    file_storage = file_storage

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_kwargs(self, step):
        """
        Provide additional keyword arguments to the form for each step.
        """
        kwargs = super().get_form_kwargs(step)

        if step == 'step3':
            # Get initial data for learning outcomes
            course_id = self.storage.extra_data.get('course_id')
            step2_data = self.get_cleaned_data_for_step('step2')
            if step2_data:
                generated_outcomes = llm.ge(course_id)
                kwargs['learning_outcomes_data'] = generated_outcomes

        return kwargs
    def get_form_initial(self, step,course=None):
        course_id = self.storage.extra_data.get('course_id')
        initial = {}
        if step == 'step2':
            step1_data = self.get_cleaned_data_for_step('step1')
            if step1_data:
                title, description = llm_instance.generate_course_title_and_description(course_id)
                initial['course_title'] = title
                initial['course_description'] = description
        elif step == 'step3':
            step2_data = self.get_cleaned_data_for_step('step2')
            if step2_data:
                generated_outcomes = llm_instance.generate_learning_outcomes(course_id)
                initial['learning_outcomes'] = json.dumps(generated_outcomes)  # Store outcomes in JSON format
                return
        elif step == 'step4':
            # Get course details from step 3
            step3_data = self.get_cleaned_data_for_step('step3')

            if step3_data:
                # Assume that course_id is saved in the session or is part of the extra data.

                generated_content = llm_instance.generate_content_listing(course_id)

                initial['content_listing'] = generated_content

        return initial

    def process_step(self, form):

        """
        Override the process_step method to save data to the database.
        """
        step = self.steps.current
        logger.info("step: " + step)
        form_data = form.cleaned_data

        # Fetch or create a course object from the extra data in storage
        extra_data = self.storage.extra_data
        course_id = extra_data.get('course_id')

        if course_id is not None:
            try:
                course = Courses.objects.get(id=int(course_id))
            except Courses.DoesNotExist:
                course = Courses()
        else:
            course = Courses()

        # Process and save data specific to each step
        if step == 'step1':
            if form_data:
                course.course_description = form_data.get('course_description', '')
                course.participants_info = form_data.get('participants_info', '')
                course.prerequisite_knowledge = form_data.get('prerequisite_knowledge', '')
                course.available_material = form_data.get('available_material', '')
                course.content_lang = form_data.get('content_lang', '')
                course.course_type = form_data.get('course_type', '')
                course.optimized_for_mooc = form_data.get('optimized_for_mooc', False)
                course.project_based = form_data.get('project_based', False)
                course.assignment = form_data.get('assignment', '')
                course.long_course_support = form_data.get('long_course_support', '')
                course.knowledge_level = form_data.get('knowledge_level', '')
                course.duration = form_data.get('duration', '')
                course.practice = form_data.get('practice', '')

        elif step == 'step2':
            course.course_title = form_data.get('course_title', '')
            course.course_description = form_data.get('course_description', '')

        elif step == 'step3':
            if form_data:
                # Update required here to make it dynamic
                number_of_outcomes = 4
                for i in range(number_of_outcomes):
                    outcome = {
                        'tag': form_data.get(f'learning_outcome_{i}_tag'),
                        'number': form_data.get(f'learning_outcome_{i}_number'),
                        'outcome': form_data.get(f'learning_outcome_{i}_outcome'),
                        'course_id':course.id,

                    }
                    if (form_data.get(f'learning_outcome_{i}_sub_items')):
                        outcome['sub_items']= form_data.get(f'learning_outcome_{i}_sub_items').split('\r\n')

                    LearningOutcome.objects.create(**outcome)

        elif step=='step4':
            content_listing = form_data.get('content_listing')
            course.save()
            if content_listing:
                # Convert the text response to JSON format

                # Load the JSON structure into a Python dict
                content_listing = json.loads(modules_listing_to_json(content_listing))

                # Iterate through each module and save it into the database
                for module_idx, module in enumerate(content_listing.get("modules", [])):
                    # Create a new ContentListing instance for each module
                    module_instance = ContentListing.objects.create(
                        course=course,
                        content_item=module["module_name"],
                        serial_number=f"module_{module_idx + 1}"
                    )

                    # Iterate through the contents in the module
                    for item_idx, item_data in enumerate(module.get("items", [])):
                        # Save each content item within the module
                        content = Content.objects.create(
                            content_listing=module_instance,
                            type=item_data.get('type'),
                            duration=item_data.get('duration'),  # Handle duration
                            key_points=item_data.get('key_points'),  # Handle key points
                            script=item_data.get('script'),  # Handle script
                            material=None,  # Assuming material is uploaded separately, keep this blank
                        )

                        # Iterate through the sub-items in the item and save them as related content
                        for sub_item_idx, sub_item in enumerate(item_data.get("sub_items", [])):
                            Content.objects.create(
                                content_listing=module_instance,
                                type="sub-item",  # Assign sub-item type
                                key_points=sub_item,  # You can use sub-item name or description for key_points
                                script="",  # No script field for sub-items, can be adjusted if needed
                                material=None,  # Assuming no material for sub-items
                            )
        # Save the course instance
        course.save()

        # Save the course ID to extra data so that we can access the same object in subsequent steps
        self.storage.extra_data['course_id'] = course.id

        return super().process_step(form)

    def done(self, form_list, **kwargs):
        """
        This method will be called when all steps are complete.
        """
        form_data = [form.cleaned_data for form in form_list]

        # Retrieve the saved course object using the session key
        course_id = self.storage.get_step_data('course_id')
        if course_id:
            course = Courses.objects.get(id=course_id)
        else:
            # If somehow the course ID is missing, we create a new instance
            course = Courses()

        # Update the course with final information if needed
        course.save()

        return render(self.request, 'course_maker/done.html', {'form_data': form_data})


# List and Create API view for Courses
class CourseListAPIView(generics.ListCreateAPIView):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer

# Retrieve, Update, and Delete API view for a specific Course
class CourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'id'

def regenerate_learning_outcome(request):
    if request.method == 'POST':
        index = int(request.POST.get('index', 0))  # Get index as an integer, default to 0 if not provided

        # Retrieve course_title and course_description based on session or database
        course_id = request.session.get('course_id')  # Assuming course_id is saved in session
        if course_id:
            try:
                course = Courses.objects.get(id=int(course_id))
                course_title = course.course_title
                course_description = course.course_description
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course not found'}, status=404)
        else:
            return JsonResponse({'error': 'Course ID not found in session'}, status=400)

        # Generate new learning outcomes
        new_outcomes = llm_instance.generate_learning_outcomes(course_title, course_description)

        # Ensure the index is within range
        if 0 <= index < len(new_outcomes):
            new_outcome = new_outcomes[index]['outcome']
            return JsonResponse({'new_outcome': new_outcome})
        else:
            return JsonResponse({'error': 'Invalid index'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


class CourseLearningOutcomesAPIView(APIView):
    def get(self, request, course_id):
        try:
            course = Courses.objects.get(id=course_id)
            learning_outcomes = course.learning_outcomes.all()
            serializer = LearningOutcomeSerializer(learning_outcomes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Courses.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

def modules_listing_to_json(content_text):
    """
    Convert Ollama's content text into JSON format.
    """

    modules = []
    current_module = None
    current_item = None

    # Regular expressions for matching modules, items, and sub-items
    module_pattern = re.compile(r"\*\*Module (\d+): (.+)\*\*")
    item_pattern = re.compile(r"- Item (\d+\.\d+): (.+) \(Type: (.+)\)")
    sub_item_pattern = re.compile(r"- Sub-item (\d+\.\d+\.\d+): (.+)")

    for line in content_text.splitlines():
        line = line.strip()  # Strip leading/trailing whitespace

        module_match = module_pattern.match(line)
        item_match = item_pattern.match(line)
        sub_item_match = sub_item_pattern.match(line)

        if module_match:
            # Start a new module
            if current_module:
                # Append the current item to the current module if it's not None
                if current_item:
                    current_module["items"].append(current_item)
                    current_item = None
                # Append the current module to the list of modules
                modules.append(current_module)

            current_module = {
                "module_name": module_match.group(2).strip(),
                "items": []
            }

        elif item_match:
            # Start a new item within the current module
            if current_module is None:
                # Handle item without a module context
                print("Warning: Found content item without a module context. Creating a generic module.")
                current_module = {
                    "module_name": "Generic Module",
                    "items": []
                }
                modules.append(current_module)

            # Append the current item to the current module if it's not None
            if current_item:
                current_module["items"].append(current_item)

            current_item = {
                "item_name": item_match.group(2).strip(),
                "type": item_match.group(3).strip(),
                "sub_items": []
            }

        elif sub_item_match:
            # Add sub-item to the current item
            if current_item is None:
                # Handle sub-item without an item context
                print("Warning: Found sub-item without a content item context. Skipping.")
                continue

            sub_item_name = sub_item_match.group(2).strip()
            current_item["sub_items"].append(sub_item_name)

    # Append the last item and module if any
    if current_item and current_module:
        current_module["items"].append(current_item)

    if current_module:
        modules.append(current_module)

    # Return the JSON structure
    return json.dumps({"modules": modules}, indent=4)

class ContentListingViewSet(viewsets.ModelViewSet):
    queryset = ContentListing.objects.all()
    serializer_class = ContentListingSerializer


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


# views.py


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

def ollama_status(request):
    try:
        system = platform.system()

        if system == "Linux" or system == "Darwin":  # For Linux/macOS
            process = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, text=True)
            if process.returncode == 0:
                status = "running"
            else:
                status = "stopped"

        elif system == "Windows":  # For Windows
            process = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"], capture_output=True, text=True)
            if "ollama.exe" in process.stdout:
                status = "running"
            else:
                status = "stopped"
        else:
            status = "unknown system"

    except Exception as e:
        status = "error"

    return JsonResponse({"status": status})


def run_ollama(request):
    try:
        system = platform.system()

        # Define the base command
        if system == "Windows":
            command = ["ollama.exe", "run", "llama3"]
        else:
            command = ["ollama", "run", "llama3"]

        # Run the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return JsonResponse({"status": "started", "message": result.stdout})

    except subprocess.CalledProcessError as e:
        return JsonResponse({"status": "error", "message": e.stderr}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
