from rest_framework import  viewsets
from .models import CourseMaterial
from .serializers import CourseMaterialSerializer
from PyPDF2 import PdfReader

class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer

    def perform_create(self, serializer):
        # Get the file from the request data
        file = self.request.FILES.get('file')

        if file:
            # Determine the file type based on the extension
            file_type = file.name.split('.')[-1].lower()

            # Read the contents of the file
            file_content = file.read().decode('utf-8') if file_type == 'txt' else 'Binary content'

            # If it's a PDF, you could use a library like PyMuPDF or PyPDF2 to extract text content
            if file_type == 'pdf':
                try:
                    pdf_reader = PdfReader(file)
                    file_content = "\n".join(
                        [page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                except Exception as e:
                    file_content = "Error reading PDF content"

            # Save the file_type and file_content in the serializer
            serializer.save(file_type=file_type, file_content=file_content)
        else:
            serializer.save()