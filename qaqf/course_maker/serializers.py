import PyPDF2
from rest_framework import serializers
from .models import Courses, LearningOutcome,Content,ContentListing,Quiz,CourseMaterial

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
            'prerequisite_knowledge', 'content_lang',
            'course_type', 'optimized_for_mooc', 'project_based', 'assignment',
            'long_course_support', 'knowledge_level', 'duration', 'practice',
            'learning_outcomes','content_listings'
        ]
class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['id', 'original_filename', 'file_type', 'file_content', 'uploaded_at', 'material_type']


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'content', 'question', 'type', 'correct_option', 'option_1', 'option_2', 'option_3', 'option_4']
