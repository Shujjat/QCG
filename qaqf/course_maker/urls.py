from django.urls import path
from .views import CourseListAPIView, CourseDetailAPIView,CourseCreationWizard,regenerate_learning_outcome


urlpatterns = [
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:id>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('api/course_creation_wizard/', CourseCreationWizard.as_view(), name='course_creation_wizard'),
    path('api/courses/', CourseListAPIView.as_view(), name='course_list'),
    path('regenerate_learning_outcome/', regenerate_learning_outcome, name='regenerate_learning_outcome'),

]