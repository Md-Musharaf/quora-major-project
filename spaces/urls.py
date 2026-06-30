from django.urls import path

from . import views

app_name = "spaces"


urlpatterns = [
    path(
        "",
        views.space_list,
        name="list",
    ),
    path(
        "create/",
        views.create_space,
        name="create",
    ),
    path(
        "<slug:slug>/",
        views.space_detail,
        name="detail",
    ),
    path(
        "<slug:slug>/edit/",
        views.edit_space,
        name="edit",
    ),
    path(
        "<slug:slug>/delete/",
        views.delete_space,
        name="delete",
    ),
    path(
        "<slug:slug>/follow/",
        views.toggle_space_follow,
        name="toggle_follow",
    ),
    path(
        "<slug:slug>/posts/create/",
        views.create_space_post,
        name="post_create",
    ),
    path(
        "<slug:slug>/posts/<int:post_id>/edit/",
        views.edit_space_post,
        name="post_edit",
    ),
    path(
        "<slug:slug>/posts/<int:post_id>/delete/",
        views.delete_space_post,
        name="post_delete",
    ),
]
