from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'api/content-listings', ContentListingViewSet)
router.register(r'api/quizzes', QuizViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:id>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('api/course_creation_wizard/', CourseCreationWizard.as_view(), name='course_creation_wizard'),
    path('api/courses/', CourseListAPIView.as_view(), name='course_list'),
    path('api/regenerate_learning_outcome/', regenerate_learning_outcome, name='regenerate_learning_outcome'),
    path('api/course/<int:course_id>/learning_outcomes/', CourseLearningOutcomesAPIView.as_view(),
         name='course-learning-outcomes'),

    path('api/ollama_status/', ollama_status, name='ollama_status'),
    path('api/run-ollama/', run_ollama, name='run_ollama'),

]