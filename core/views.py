from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Q,
    Value,
)
from django.shortcuts import render

from interactions.models import QuestionVote
from questions.models import Question

from topics.models import Topic
from users.models import User


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


def search(request):
    query = request.GET.get("q", "").strip()

    questions = Question.objects.none()
    users = User.objects.none()
    topics = Topic.objects.none()

    if query:
        questions = (
            Question.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            .select_related(
                "author",
                "author__profile",
            )
            .prefetch_related("topics")
            .order_by("-created_at")
        )

        users = (
            User.objects.filter(
                Q(profile__display_name__icontains=query)
                | Q(profile__profession__icontains=query)
                | Q(email__icontains=query)
            )
            .select_related("profile")
            .order_by("profile__display_name")
        )

        topics = Topic.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by("name")

    context = {
        "query": query,
        "questions": questions,
        "users": users,
        "topics": topics,
    }

    return render(
        request,
        "core/search_results.html",
        context,
    )
