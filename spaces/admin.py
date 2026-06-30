from django.contrib import admin

from .models import Space, SpaceFollow, SpacePost


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__profile__display_name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    filter_horizontal = ("topics",)


@admin.register(SpaceFollow)
class SpaceFollowAdmin(admin.ModelAdmin):
    list_display = (
        "space",
        "user",
        "followed_at",
    )

    list_filter = ("followed_at",)

    search_fields = (
        "space__name",
        "user__email",
        "user__profile__display_name",
    )


@admin.register(SpacePost)
class SpacePostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "space",
        "author",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "content",
        "space__name",
        "author__email",
        "author__profile__display_name",
    )

    list_select_related = (
        "space",
        "author",
    )
