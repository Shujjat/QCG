from rest_framework import serializers
from .models import Courses, LearningOutcome,Content,ContentListing

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
            'prerequisite_knowledge', 'available_material', 'content_lang',
            'course_type', 'optimized_for_mooc', 'project_based', 'assignment',
            'long_course_support', 'knowledge_level', 'duration', 'practice',
            'learning_outcomes','content_listings'
        ]
