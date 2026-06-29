from django.contrib import admin

from .models import Topic, TopicFollow


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(TopicFollow)
class TopicFollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "topic",
        "created_at",
    )

    list_filter = (
        "topic",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__profile__display_name",
        "topic__name",
    )

    raw_id_fields = (
        "user",
        "topic",
    )
