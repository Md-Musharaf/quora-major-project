from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path(
        "questions/<int:question_id>/vote/",
        views.toggle_question_vote,
        name="toggle_question_vote",
    ),
    path(
        "answers/<int:answer_id>/vote/",
        views.toggle_answer_vote,
        name="toggle_answer_vote",
    ),
]
