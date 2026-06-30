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

from questions.documents import QuestionDocument
from topics.documents import TopicDocument
from users.documents import UserDocument


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
        question_search = QuestionDocument.search().query(
            "multi_match",
            query=query,
            fields=[
                "title^4",
                "description^2",
                "topics.name^3",
                "author.display_name^2",
                "author.profession",
            ],
            fuzziness="AUTO",
        )[:50]

        questions = (
            question_search.to_queryset()
            .select_related(
                "author",
                "author__profile",
            )
            .prefetch_related("topics")
        )

        user_search = UserDocument.search().query(
            {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "display_name^4",
                                    "profession^3",
                                    "bio^2",
                                    "location",
                                ],
                                "fuzziness": "AUTO",
                            }
                        },
                        {
                            "wildcard": {
                                "email": {
                                    "value": f"*{query.lower()}*",
                                    "case_insensitive": True,
                                }
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            }
        )[:30]

        users = user_search.to_queryset().select_related("profile")

        topic_search = TopicDocument.search().query(
            "multi_match",
            query=query,
            fields=[
                "name^4",
                "description^2",
            ],
            fuzziness="AUTO",
        )[:30]

        topics = topic_search.to_queryset()

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
