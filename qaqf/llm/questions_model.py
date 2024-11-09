from django.db import models
from django.conf import settings


class UserQuestionLog(models.Model):
    # Foreign key to the Courses model (assuming you have a Courses model)
    course_id = models.ForeignKey('course_maker.Courses', on_delete=models.CASCADE, related_name='user_questions')

    # User who asked the question (assuming you have Django's default User model)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_questions')

    # User's question text
    user_question = models.TextField("User Question")
    response_to_question = models.TextField("Response to Question")

    # Date and time when the question was asked
    datetime = models.DateTimeField("Timestamp", auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user_id} on Course {self.course_id}: {self.user_question[:50]}"
