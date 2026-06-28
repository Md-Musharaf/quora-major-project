from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Comment(models.Model):
    answer = models.ForeignKey(
        "questions.Answer",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_comments",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    content = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["answer", "parent", "created_at"],
                name="comment_thread_index",
            ),
        ]

    def clean(self):
        super().clean()

        if self.parent and self.parent.answer_id != self.answer_id:
            raise ValidationError(
                {"parent": ("A reply must belong to a comment under the same answer.")}
            )

        if self.parent_id and self.parent_id == self.id:
            raise ValidationError({"parent": "A comment cannot be a reply to itself."})

    @property
    def is_reply(self):
        return self.parent_id is not None

    def __str__(self):
        return f"Comment by {self.author} on answer {self.answer_id}"
