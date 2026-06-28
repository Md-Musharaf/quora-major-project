from django.conf import settings
from django.db import models

from questions.models import Answer, Question


class QuestionVote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_votes",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="votes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"],
                name="unique_question_vote",
            )
        ]

    def __str__(self):
        return f"{self.user} voted on {self.question}"


class AnswerVote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_votes",
    )

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="votes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "answer"],
                name="unique_answer_vote",
            )
        ]

    def __str__(self):
        return f"{self.user} voted on answer {self.answer_id}"