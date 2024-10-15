
# views.py

from rest_framework import viewsets
from .models import Log
from .serializers import LogSerializer

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all().order_by('-timestamp')
    serializer_class = LogSerializer