import os
import yt_dlp
import boto3
from rest_framework import  viewsets
import requests
import speech_recognition as sr
from PyPDF2 import PdfReader
from pydub import AudioSegment
from .models import CourseMaterial
from .serializers import CourseMaterialSerializer
APP_FOLDER = os.path.dirname(os.path.dirname(__file__))
#need to retrieve it from .env
youtube_output_path = os.path.join(os.path.dirname(APP_FOLDER), 'qaqf/media/audio_books/temp_youtube_audio')

class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer

    def perform_create(self, serializer):
        # Get the file and audiobook URL from the request data
        file = self.request.FILES.get('file')
        audio_book_url = self.request.data.get('audio_book')

        file_content = None  # Initialize file_content

        if file:
            # Process file based on file type
            file_type = file.name.split('.')[-1].lower()
            if file_type == 'txt':
                file_content = file.read().decode('utf-8')
            elif file_type == 'pdf':
                file_content = self.extract_pdf_content(file)

            serializer.save(file_type=file_type, file_content=file_content)

        elif audio_book_url:
            # Process audiobook URL if provided
            if "youtube.com" in audio_book_url or "youtu.be" in audio_book_url:
                self.download_audio_from_youtube(audio_book_url)

                pass

            #ToDo
            # Testing is required for this
            elif audio_book_url.startswith("s3://"):
                audio_path = self.download_audio_from_aws(audio_book_url)
            else:
                audio_path = self.download_audio(audio_book_url)  # General URL handler
            audio_path=youtube_output_path
            if audio_path:
                wav_path = self.convert_to_wav(audio_path+'.mp3')
                if wav_path:
                    file_content = self.convert_audio_to_text(wav_path)
                    os.remove(wav_path)  # Clean up
                    os.remove(audio_path+'.mp3')  # Clean up original download

            serializer.save(
                file_type='audiobook',
                file_content=file_content,
                audio_book=audio_book_url,

            )
        else:
            serializer.save()

    def extract_pdf_content(self, file):
        try:
            pdf_reader = PdfReader(file)
            return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        except Exception:
            return "Error reading PDF content"

    def download_audio_from_youtube(self, url):
        """Download audio from YouTube and return the path to the file."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': youtube_output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'timeout': 60*5,
            'nocheckcertificate': True,
            'noprogress': True,
            'consoletitle': False,
            'http_chunk_size': 1048576,  # 1MB chunks
            'range': False,  # Avoids range requests

        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_audio_from_aws(self, s3_url):
        """Download audio from AWS S3 bucket and return the file path."""
        s3 = boto3.client('s3')
        bucket_name, key = s3_url.replace("s3://", "").split("/", 1)
        local_path = "temp_s3_audio.mp3"
        s3.download_file(bucket_name, key, local_path)
        return local_path

    def download_audio(self, url):
        """Download audio file from a general URL."""
        response = requests.get(url)
        if response.status_code == 200:
            audio_path = "temp_audio_file.mp3"
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)
            return audio_path
        return None

    def convert_to_wav(self, audio_path):
        """Convert audio to WAV format and return the path."""
        try:
            wav_path = "temp_audio_file.wav"
            sound = AudioSegment.from_file(audio_path)
            sound.export(wav_path, format="wav")
            return wav_path
        except Exception as e:
            print(f"Error converting to WAV: {e}")
            return None

    def convert_audio_to_text(self, wav_path):
        """Convert audio in WAV format to text using SpeechRecognition."""
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Audio not clear enough for transcription."
        except sr.RequestError as e:
            return f"Could not request results; {e}"