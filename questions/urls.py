from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path(
        "ask/",
        views.create_question,
        name="create_question",
    ),
    path(
        "<int:question_id>/",
        views.question_detail,
        name="detail",
    ),
    path(
        "<int:question_id>/edit/",
        views.edit_question,
        name="edit",
    ),
    path(
        "<int:question_id>/delete/",
        views.delete_question,
        name="delete",
    ),
    path(
        "answers/<int:answer_id>/edit/",
        views.edit_answer,
        name="edit_answer",
    ),
    path(
        "answers/<int:answer_id>/delete/",
        views.delete_answer,
        name="delete_answer",
    ),
]
