from django.urls import path

from . import views

app_name = "topics"

urlpatterns = [
    path(
        "<slug:slug>/",
        views.topic_detail,
        name="detail",
    ),
    path(
        "<slug:slug>/follow/",
        views.toggle_topic_follow,
        name="toggle_follow",
    ),
]
