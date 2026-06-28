from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "description",
        "author__email",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)