from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import render
from .serializers import LogSerializer
from .maki_serializers import MakiSerializer
from course_maker.models  import Courses
from course_maker.views import llm_instance
from llm.llm import LLM
from .models import Log
from .questions_model import UserQuestionLog

# Create a dummy user if one doesn't already exist (for example purposes)



llm_instance=LLM()
class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all().order_by('-timestamp')
    serializer_class = LogSerializer


class MakiViewSet(viewsets.ModelViewSet):
    serializer_class = MakiSerializer  # Provide the serializer class

    def get_queryset(self):
        # Since this ViewSet does not use a specific model, we return an empty list.
        return []

    def get_serializer_class(self):
        return self.serializer_class

    # Example list action to test the ViewSet
    def list(self, request):
        pass

    @action(detail=False, methods=['get', 'post'], )
    def ask_maki(self, request):
        """
        This action receives a course_id from the request and performs operations on CourseMaterial.

        """
        if request.method == 'GET':
            # Render the HTML form if the request is GET
            return render(request, 'llm/ask_maki.html')

        elif request.method == 'POST':
            # Process the form data if the request is POST
            course_id = request.data.get('course_id')
            user_question = request.data.get('user_question')

            # Check if the course_id is provided
            if not course_id:
                return Response({"error": "course_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate if the course exists
            try:
                course = Courses.objects.get(id=course_id)
            except Courses.DoesNotExist:
                return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

            response= llm_instance.ask_question(course, user_question)
            # Prepare the response

            #Todo
            # use proper user later.
            #user = self.request.user
            dummy_user, created = User.objects.get_or_create(username="dummy_user")

            _ = UserQuestionLog.objects.create(
                                                            course_id=course,
                                                            user_id=dummy_user,
                                                            user_question=user_question,
                                                            response_to_question=response
                                                            )

            response_data = {
                "course_id": course.id,
                "course_title": course.course_title,
                "response":response
            }

            return Response(response_data, status=status.HTTP_200_OK)
