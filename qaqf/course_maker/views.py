# course_maker/views.py
import json
from rest_framework.views import APIView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from .course_wizard_forms import *
from rest_framework import generics
from rest_framework.response import Response
from .models import Courses, LearningOutcome
from .serializers import CourseSerializer,LearningOutcomeSerializer
from .ollama_helper import *
from rest_framework import status


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
            step2_data = self.get_cleaned_data_for_step('step2')
            if step2_data:
                course_title = step2_data.get('course_title')
                course_description = step2_data.get('course_description')
                generated_outcomes = generate_learning_outcomes(course_title, course_description)
                kwargs['learning_outcomes_data'] = generated_outcomes

        return kwargs
    def get_form_initial(self, step):
        """
        Populate initial data for forms.
        """
        initial = {}

        # For step 2, set initial values for 'course_title' and 'generated_course_description'
        if step == 'step2':
            step1_data = self.get_cleaned_data_for_step('step1')
            if step1_data:
                title, description = generate_course_title_and_description(step1_data)
                initial['course_title'] = title
                initial['course_description'] = description

        # For step 3, generate initial learning outcomes if available
        elif step == 'step3':
            step2_data = self.get_cleaned_data_for_step('step2')
            if step2_data:
                course_title = step2_data.get('course_title')
                course_description = step2_data.get('course_description')
                generated_outcomes = generate_learning_outcomes(course_title, course_description)
                initial['learning_outcomes'] = json.dumps(generated_outcomes)  # Store outcomes in JSON format

        return initial

    def process_step(self, form):

        """
        Override the process_step method to save data to the database.
        """
        step = self.steps.current
        print('step:'+str(step))
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
            print(form_data)
            if form_data:

                number_of_outcomes = 4


                for i in range(number_of_outcomes):
                    outcome = {
                        'tag': form_data.get(f'learning_outcome_{i}_tag'),
                        'number': form_data.get(f'learning_outcome_{i}_number'),
                        'outcome': form_data.get(f'learning_outcome_{i}_outcome'),
                        'course_id':course.id
                       # 'sub_items': form_data.get(f'learning_outcome_{i}_sub_items').split('\r\n'),

                    }
                    LearningOutcome.objects.create(**outcome)

                else:

                       pass



        elif step=='step4':
            print("in step 4")
            if form_data:
                print("if form_data:")
                for key, value in form_data.items():
                    print(" for key, value in form_data.items():")
                    if key.startswith('tag_'):
                        print(" if key.startswith('tag_'):")
                        index = key.split('_')[1]
                        tag = form_data[f'tag_{index}']
                        number = form_data[f'number_{index}']
                        outcome_text = form_data[f'outcome_{index}']
                        sub_items = form_data.get(f'sub_items_{index}', '')

                        # Save each learning outcome to the database
                        LearningOutcome.objects.create(
                            course=course,
                            outcome=outcome_text,
                            tag=tag,
                            number=int(number)
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
        new_outcomes = generate_learning_outcomes(course_title, course_description)

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