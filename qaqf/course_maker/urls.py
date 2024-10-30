from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('api/course-materials', CourseMaterialViewSet)
router.register(r'api/content-listings', ContentListingViewSet)
router.register(r'api/quizzes', QuizViewSet)
router.register(r'api/regenerate', CourseViewSet,basename='api')
urlpatterns = [
    path('', include(router.urls)),
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:id>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('api/course_creation_wizard/', CourseCreationWizard.as_view(), name='course_creation_wizard'),
    path('api/courses/', CourseListAPIView.as_view(), name='course_list'),
    path('api/course/<int:course_id>/learning_outcomes/', CourseLearningOutcomesAPIView.as_view(),
         name='course-learning-outcomes-list'),  # List all outcomes
    path('api/course/<int:course_id>/learning_outcomes/<int:outcome_id>/', CourseLearningOutcomesAPIView.as_view(),
         name='course-learning-outcome-detail'),  # Retrieve, delete specific outcome
    # path('courses/<int:course_id>/materials/', CourseMaterialListCreateView.as_view(), name='course-materials'),
    # path('courses/<int:course_id>/materials/<int:material_id>/', CourseMaterialDetailView.as_view(), name='course-material-detail'),
    path('api/ollama_status/', ollama_status, name='ollama_status'),
    #path('api/run-ollama/', run_ollama, name='run_ollama'),

]