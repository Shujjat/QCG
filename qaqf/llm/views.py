from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import render
from gtts import gTTS
import os
import pyttsx3
from django.conf import settings

##########################################
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
            as_audio = request.data.get('as_audio')
            as_audio=True

            response= llm_instance.ask_question(course, user_question)
            # Prepare the response

            #Todo
            # use proper user later.
            #user = self.request.user
            dummy_user, created = User.objects.get_or_create(username="dummy_user")

            question = UserQuestionLog.objects.create(
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
            if as_audio:
                audio_path = self.generate_audio(response, voice_name=voice_name, rate=rate, volume=volume)
                if audio_path:
                    audio_url = f"{settings.MEDIA_URL}tts_audio/{os.path.basename(audio_path)}"
                    response_data["audio_url"] = audio_url

    def generate_audio(file_name=None,response_text, voice_name=None, rate=200, volume=1.0):
        """
        Generates an audio file from text using pyttsx3 with customizable options.

        Args:
            response_text (str): The text to convert to speech.
            voice_name (str): The name of the voice (optional).
            rate (int): Speed of the speech (default is 200).
            volume (float): Volume level (between 0.0 and 1.0).

        Returns:
            str: The file path of the generated audio.
        """
        try:
            # Initialize pyttsx3 engine
            engine = pyttsx3.init()

            # Set properties
            engine.setProperty('rate', rate)  # Speed of speech
            engine.setProperty('volume', volume)  # Volume level (0.0 to 1.0)

            # List available voices
            voices = engine.getProperty('voices')

            # Set a specific voice if provided
            if voice_name:
                selected_voice = next((voice for voice in voices if voice_name.lower() in voice.name.lower()), None)
                if selected_voice:
                    engine.setProperty('voice', selected_voice.id)
                else:
                    print(f"Voice '{voice_name}' not found. Using default voice.")

            # Generate unique filename
            filename = f"{uuid.uuid4()}.mp3"
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'tts_audio')
            os.makedirs(audio_dir, exist_ok=True)
            file_path = os.path.join(audio_dir, filename)

            # Save the audio to file
            engine.save_to_file(response_text, file_path)
            engine.runAndWait()

            return file_path
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None