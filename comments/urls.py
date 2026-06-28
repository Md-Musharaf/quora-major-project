from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path(
        "answers/<int:answer_id>/comments/create/",
        views.create_comment,
        name="create_comment",
    ),
    path(
        "<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
]
