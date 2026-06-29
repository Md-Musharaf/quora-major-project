from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Value,
)
from django.shortcuts import render

from interactions.models import QuestionVote
from questions.models import Question


def home(request):
    questions = (
        Question.objects.select_related(
            "author",
            "author__profile",
        )
        .annotate(
            answer_count=Count("answers", distinct=True),
            vote_count=Count("votes", distinct=True),
        )
        .prefetch_related("topics")
        .order_by("-created_at")
    )

    if request.user.is_authenticated:
        questions = questions.annotate(
            user_has_voted=Exists(
                QuestionVote.objects.filter(
                    question_id=OuterRef("pk"),
                    user=request.user,
                )
            )
        )
    else:
        questions = questions.annotate(
            user_has_voted=Value(
                False,
                output_field=BooleanField(),
            )
        )

    context = {
        "questions": questions,
    }

    return render(request, "core/home.html", context)
