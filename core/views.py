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

from search_engine.search import (
    get_question_search_queryset,
    get_topic_search_queryset,
    get_user_search_queryset,
)


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

    search_query = request.GET.get("q", "").strip()

    if search_query:
        questions = questions.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(topics__name__icontains=search_query)
        ).distinct()

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
        "search_query": search_query,
    }

    return render(request, "core/home.html", context)


def search(request):
    query = request.GET.get("q", "").strip()

    questions = Question.objects.none()
    users = User.objects.none()
    topics = Topic.objects.none()

    if query:
        questions = get_question_search_queryset(
            query,
            limit=50,
        )

        users = get_user_search_queryset(
            query,
            limit=50,
        )

        topics = get_topic_search_queryset(
            query,
            limit=50,
        )

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
