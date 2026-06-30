from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Space(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_spaces",
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.ImageField(
        upload_to="spaces/icons/",
        blank=True,
        null=True,
    )

    cover_image = models.ImageField(
        upload_to="spaces/covers/",
        blank=True,
        null=True,
    )

    topics = models.ManyToManyField(
        "topics.Topic",
        related_name="spaces",
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "spaces:detail",
            kwargs={"slug": self.slug},
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.name)
            slug = original_slug
            counter = 1

            while Space.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class SpaceFollow(models.Model):
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="follows",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_spaces",
    )

    followed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["space", "user"],
                name="unique_space_follow",
            )
        ]

        ordering = ["-followed_at"]

    def __str__(self):
        return f"{self.user} follows {self.space}"


class SpacePost(models.Model):
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="space_posts",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
    )

    content = models.TextField()

    image = models.ImageField(
        upload_to="spaces/posts/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.title:
            return self.title

        return f"Post by {self.author} in {self.space}"
