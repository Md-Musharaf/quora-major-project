import logging
from typing import Any

from django.conf import settings
from django.db.models import (
    Case,
    IntegerField,
    Q,
    QuerySet,
    Value,
    When,
)

from questions.models import Question

from .client import get_elasticsearch_client

from django.contrib.auth import get_user_model

from topics.models import Topic

logger = logging.getLogger(__name__)
User = get_user_model()


def normalize_search_limit(limit: int) -> int:
    """
    Keep the Elasticsearch result limit within a safe range.
    """
    return max(1, min(limit, 100))


def execute_id_search(
    *,
    index_name: str,
    query: dict,
    limit: int,
) -> list[int]:
    """
    Run an Elasticsearch query and return document IDs
    in relevance order.
    """
    client = get_elasticsearch_client()

    response = client.options(
        request_timeout=3,
        max_retries=0,
    ).search(
        index=index_name,
        size=normalize_search_limit(limit),
        query=query,
    )

    result_ids = []

    for hit in response["hits"]["hits"]:
        source = hit.get("_source", {})

        result_ids.append(int(source.get("id", hit["_id"])))

    return result_ids


def build_relevance_order(object_ids: list[int]) -> Case:
    """
    Build a SQL CASE expression that preserves Elasticsearch order.
    """
    return Case(
        *[
            When(
                pk=object_id,
                then=Value(position),
            )
            for position, object_id in enumerate(object_ids)
        ],
        default=Value(len(object_ids)),
        output_field=IntegerField(),
    )


def search_question_documents(
    search_text: str,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Search question documents in Elasticsearch.

    Results are returned in Elasticsearch relevance order.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return []

    limit = max(1, min(limit, 100))

    client = get_elasticsearch_client()

    response = client.options(
        request_timeout=3,
        max_retries=0,
    ).search(
        index=settings.ELASTICSEARCH_QUESTION_INDEX,
        size=limit,
        query={
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "title": {
                                "query": normalized_query,
                                "boost": 8,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": normalized_query,
                            "fields": [
                                "title^5",
                                "topics^3",
                                "author_name^2",
                                "description",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                            "prefix_length": 1,
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    )

    results = []

    for hit in response["hits"]["hits"]:
        source = hit.get("_source", {})

        results.append(
            {
                "id": int(source.get("id", hit["_id"])),
                "score": hit.get("_score", 0),
                "title": source.get("title", ""),
                "description": source.get(
                    "description",
                    "",
                ),
                "topics": source.get("topics", []),
                "author_name": source.get(
                    "author_name",
                    "",
                ),
            }
        )

    return results


def search_question_ids(
    search_text: str,
    *,
    limit: int = 50,
) -> list[int]:
    """
    Return matching question IDs in Elasticsearch relevance order.
    """
    results = search_question_documents(
        search_text,
        limit=limit,
    )

    return [result["id"] for result in results]


def get_base_question_queryset() -> QuerySet:
    """
    Return the optimized queryset used by the search page.
    """
    return Question.objects.select_related(
        "author",
        "author__profile",
    ).prefetch_related("topics")


def postgres_question_search(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search questions using PostgreSQL.

    This is used when Elasticsearch is disabled or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return Question.objects.none()

    return (
        get_base_question_queryset()
        .filter(
            Q(title__icontains=normalized_query)
            | Q(description__icontains=normalized_query)
            | Q(topics__name__icontains=normalized_query)
            | Q(author__profile__display_name__icontains=(normalized_query))
        )
        .distinct()
        .order_by("-created_at")[:limit]
    )


def get_questions_in_relevance_order(
    question_ids: list[int],
) -> QuerySet:
    """
    Load complete Question objects from PostgreSQL while preserving
    Elasticsearch relevance order.
    """
    if not question_ids:
        return Question.objects.none()

    relevance_order = Case(
        *[
            When(
                pk=question_id,
                then=Value(position),
            )
            for position, question_id in enumerate(question_ids)
        ],
        default=Value(len(question_ids)),
        output_field=IntegerField(),
    )

    return (
        get_base_question_queryset()
        .filter(pk__in=question_ids)
        .annotate(
            search_relevance_order=relevance_order,
        )
        .order_by("search_relevance_order")
    )


def get_question_search_queryset(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search using Elasticsearch and return complete Django objects.

    PostgreSQL is used automatically when Elasticsearch is disabled
    or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return Question.objects.none()

    if not settings.ELASTICSEARCH_ENABLED:
        return postgres_question_search(
            normalized_query,
            limit=limit,
        )

    try:
        question_ids = search_question_ids(
            normalized_query,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "Elasticsearch question search failed. " "Using PostgreSQL fallback."
        )

        return postgres_question_search(
            normalized_query,
            limit=limit,
        )

    return get_questions_in_relevance_order(
        question_ids,
    )


def search_user_ids(
    search_text: str,
    *,
    limit: int = 50,
) -> list[int]:
    """
    Search users in Elasticsearch and return IDs
    in relevance order.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return []

    return execute_id_search(
        index_name=settings.ELASTICSEARCH_USER_INDEX,
        limit=limit,
        query={
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "display_name": {
                                "query": normalized_query,
                                "boost": 8,
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "email": {
                                "query": normalized_query,
                                "boost": 5,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": normalized_query,
                            "fields": [
                                "display_name^5",
                                "profession^3",
                                "email^3",
                                "location^2",
                                "bio",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                            "prefix_length": 1,
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    )


def get_base_user_queryset() -> QuerySet:
    """
    Return users with their profiles loaded.
    """
    return User.objects.select_related("profile")


def postgres_user_search(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search users through PostgreSQL when Elasticsearch
    is disabled or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return User.objects.none()

    return (
        get_base_user_queryset()
        .filter(
            Q(email__icontains=normalized_query)
            | Q(profile__display_name__icontains=(normalized_query))
            | Q(profile__profession__icontains=(normalized_query))
            | Q(profile__bio__icontains=normalized_query)
            | Q(profile__location__icontains=(normalized_query))
        )
        .order_by(
            "profile__display_name",
            "email",
        )[:limit]
    )


def get_users_in_relevance_order(
    user_ids: list[int],
) -> QuerySet:
    """
    Load complete users from PostgreSQL while preserving
    Elasticsearch relevance order.
    """
    if not user_ids:
        return User.objects.none()

    relevance_order = build_relevance_order(user_ids)

    return (
        get_base_user_queryset()
        .filter(pk__in=user_ids)
        .annotate(
            search_relevance_order=relevance_order,
        )
        .order_by("search_relevance_order")
    )


def get_user_search_queryset(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search users with Elasticsearch.

    Fall back to PostgreSQL if Elasticsearch is disabled
    or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return User.objects.none()

    if not settings.ELASTICSEARCH_ENABLED:
        return postgres_user_search(
            normalized_query,
            limit=limit,
        )

    try:
        user_ids = search_user_ids(
            normalized_query,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "Elasticsearch user search failed. " "Using PostgreSQL fallback."
        )

        return postgres_user_search(
            normalized_query,
            limit=limit,
        )

    return get_users_in_relevance_order(user_ids)


def get_user_search_queryset(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search users with Elasticsearch.

    Fall back to PostgreSQL if Elasticsearch is disabled
    or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return User.objects.none()

    if not settings.ELASTICSEARCH_ENABLED:
        return postgres_user_search(
            normalized_query,
            limit=limit,
        )

    try:
        user_ids = search_user_ids(
            normalized_query,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "Elasticsearch user search failed. " "Using PostgreSQL fallback."
        )

        return postgres_user_search(
            normalized_query,
            limit=limit,
        )

    return get_users_in_relevance_order(user_ids)


def postgres_topic_search(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search topics through PostgreSQL when Elasticsearch
    is disabled or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return Topic.objects.none()

    return Topic.objects.filter(
        Q(name__icontains=normalized_query) | Q(description__icontains=normalized_query)
    ).order_by("name")[:limit]


def get_topics_in_relevance_order(
    topic_ids: list[int],
) -> QuerySet:
    """
    Load complete topics from PostgreSQL while preserving
    Elasticsearch relevance order.
    """
    if not topic_ids:
        return Topic.objects.none()

    relevance_order = build_relevance_order(topic_ids)

    return (
        Topic.objects.filter(pk__in=topic_ids)
        .annotate(
            search_relevance_order=relevance_order,
        )
        .order_by("search_relevance_order")
    )


def search_topic_ids(
    search_text: str,
    *,
    limit: int = 50,
) -> list[int]:
    """
    Search topics in Elasticsearch and return IDs
    in relevance order.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return []

    return execute_id_search(
        index_name=settings.ELASTICSEARCH_TOPIC_INDEX,
        limit=limit,
        query={
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "name": {
                                "query": normalized_query,
                                "boost": 8,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": normalized_query,
                            "fields": [
                                "name^5",
                                "description",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                            "prefix_length": 1,
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    )


def get_topic_search_queryset(
    search_text: str,
    *,
    limit: int = 50,
) -> QuerySet:
    """
    Search topics with Elasticsearch.

    Fall back to PostgreSQL if Elasticsearch is disabled
    or unavailable.
    """
    normalized_query = search_text.strip()

    if not normalized_query:
        return Topic.objects.none()

    if not settings.ELASTICSEARCH_ENABLED:
        return postgres_topic_search(
            normalized_query,
            limit=limit,
        )

    try:
        topic_ids = search_topic_ids(
            normalized_query,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "Elasticsearch topic search failed. " "Using PostgreSQL fallback."
        )

        return postgres_topic_search(
            normalized_query,
            limit=limit,
        )

    return get_topics_in_relevance_order(topic_ids)
