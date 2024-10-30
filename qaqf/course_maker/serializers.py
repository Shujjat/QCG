import PyPDF2
from rest_framework import serializers
from .models import Courses, LearningOutcome,Content,ContentListing,Quiz

class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = ['id', 'tag', 'number', 'outcome', 'sub_items']



class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'


class ContentListingSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = ContentListing
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    learning_outcomes = LearningOutcomeSerializer(many=True, read_only=True)
    content_listings = ContentListingSerializer(many=True, read_only=True)

    class Meta:
        model = Courses
        fields = [
            'id', 'course_title', 'course_description', 'participants_info',
            'prerequisite_knowledge', 'available_material','available_material_content', 'content_lang',
            'course_type', 'optimized_for_mooc', 'project_based', 'assignment',
            'long_course_support', 'knowledge_level', 'duration', 'practice',
            'learning_outcomes','content_listings'
        ]

    def extract_pdf_content(self, pdf_file):
        """Helper method to extract content from a PDF file."""
        content = ''
        try:
            # Create a PDF reader object using PyPDF2
            reader = PyPDF2.PdfReader(pdf_file)
            # Extract all text from the PDF
            for page in range(len(reader.pages)):
                content += reader.pages[page].extract_text()
        except Exception as e:
            content = f"Error reading PDF: {str(e)}"
        return content.strip()

    def create(self, validated_data):
        # Check if 'available_material' is provided in the request
        pdf_file = validated_data.get('available_material', None)
        print("inside create")
        print(pdf_file)
        # Create the course instance
        course = Courses.objects.create(**validated_data)

        # If there is a PDF file, extract the content and save it to the instance
        if pdf_file:
            extracted_content = self.extract_pdf_content(pdf_file)
            course.available_material_content = extracted_content
            course.save()

        return course

    def update(self, instance, validated_data):
        # Handle updating the instance fields
        pdf_file = validated_data.get('available_material', None)

        # Update the existing instance with new validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If there is a PDF file, extract the content and update the instance
        if pdf_file:
            extracted_content = self.extract_pdf_content(pdf_file)
            print("inside serializer")
            instance.available_material_content = extracted_content

        # Save the updated instance
        instance.save()
        return instance


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'content', 'question', 'type', 'correct_option', 'option_1', 'option_2', 'option_3', 'option_4']
