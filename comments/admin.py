from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "answer",
        "parent",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "content",
        "author__email",
        "author__profile__display_name",
    )

    raw_id_fields = (
        "answer",
        "author",
        "parent",
    )
