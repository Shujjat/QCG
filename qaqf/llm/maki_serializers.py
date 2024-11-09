from rest_framework import serializers

class MakiSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    message = serializers.CharField(max_length=100, default="")
