from django.urls import path
from .views import *


urlpatterns = [
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:id>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('api/course_creation_wizard/', CourseCreationWizard.as_view(), name='course_creation_wizard'),
    path('api/courses/', CourseListAPIView.as_view(), name='course_list'),
    path('api/regenerate_learning_outcome/', regenerate_learning_outcome, name='regenerate_learning_outcome'),
    path('api/course/<int:course_id>/learning_outcomes/', CourseLearningOutcomesAPIView.as_view(),
         name='course-learning-outcomes'),
    path('api/content-listings/', ContentListingAPIView.as_view(), name='content-listing-list'),
    path('api/content-listings/<int:pk>/', ContentListingDetailAPIView.as_view(), name='content-listing-detail'),
    # Content endpoints
    path('api/contents/', ContentAPIView.as_view(), name='content-list'),
    path('api/contents/<int:pk>/', ContentDetailAPIView.as_view(), name='content-detail'),

]