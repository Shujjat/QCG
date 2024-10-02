from rest_framework import serializers
from .models import Courses, LearningOutcome

class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = ['id', 'tag', 'number', 'outcome']#, 'sub_items']


class CourseSerializer(serializers.ModelSerializer):
    learning_outcomes = LearningOutcomeSerializer(many=True, read_only=True)

    class Meta:
        model = Courses
        fields = [
            'id', 'course_title', 'course_description', 'participants_info',
            'prerequisite_knowledge', 'available_material', 'content_lang',
            'course_type', 'optimized_for_mooc', 'project_based', 'assignment',
            'long_course_support', 'knowledge_level', 'duration', 'practice',
            'learning_outcomes'
        ]
