from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("users/", include("users.urls")),
    path("questions/", include("questions.urls")),
    path("interactions/", include("interactions.urls")),
    path("comments/", include("comments.urls")),
    path("topics/", include("topics.urls")),
    path("spaces/", include("spaces.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
