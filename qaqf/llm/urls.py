# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogViewSet,MakiViewSet

router = DefaultRouter()
router.register(r'logs', LogViewSet)
router.register(r'ask_maki', MakiViewSet, basename='maki')
urlpatterns = [
    path('api/', include(router.urls)),

]
