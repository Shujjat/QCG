from rest_framework import serializers
from .models import CourseMaterial
class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['id','course','file_type', 'file', 'original_filename', 'file_content', 'uploaded_at', 'material_type']

