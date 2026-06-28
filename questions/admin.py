from django.contrib import admin

from .models import Answer, Question


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


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "short_content",
        "question",
        "author",
        "created_at",
    )

    search_fields = (
        "content",
        "question__title",
        "author__email",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    def short_content(self, obj):
        return obj.content[:50]

    short_content.short_description = "Answer"
