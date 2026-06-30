from django.contrib.auth import get_user_model
from topics.models import Topic

from typing import Any

from django.conf import settings
from elasticsearch import NotFoundError
from elasticsearch.helpers import bulk

from questions.models import Question

from .client import get_elasticsearch_client
from .documents import (
    question_to_document,
    topic_to_document,
    user_to_document,
)

User = get_user_model()


def get_question_queryset():
    """
    Return questions with related data loaded efficiently.
    """
    return (
        Question.objects.select_related(
            "author",
            "author__profile",
        )
        .prefetch_related("topics")
        .order_by("pk")
    )


def index_question(
    question: Question,
    *,
    refresh: bool | str = False,
) -> dict[str, Any]:
    """
    Create or replace one question document in Elasticsearch.

    Using the question ID as the Elasticsearch document ID prevents
    duplicate documents when the same question is indexed again.
    """
    client = get_elasticsearch_client()

    response = client.index(
        index=settings.ELASTICSEARCH_QUESTION_INDEX,
        id=str(question.pk),
        document=question_to_document(question),
        refresh=refresh,
    )

    return dict(response)


def delete_question_document(
    question_id: int,
    *,
    refresh: bool | str = False,
) -> bool:
    """
    Delete one question document from Elasticsearch.

    Returns True when a document was deleted and False when it did
    not exist.
    """
    client = get_elasticsearch_client()

    try:
        client.delete(
            index=settings.ELASTICSEARCH_QUESTION_INDEX,
            id=str(question_id),
            refresh=refresh,
        )
    except NotFoundError:
        return False

    return True


def generate_question_bulk_actions(queryset):
    """
    Yield Elasticsearch bulk-indexing actions one at a time.
    """
    index_name = settings.ELASTICSEARCH_QUESTION_INDEX

    for question in queryset.iterator(chunk_size=500):
        yield {
            "_op_type": "index",
            "_index": index_name,
            "_id": str(question.pk),
            "_source": question_to_document(question),
        }


def bulk_index_questions(
    queryset=None,
    *,
    refresh: bool | str = False,
) -> tuple[int, list]:
    """
    Index multiple questions efficiently.

    Returns:
        A tuple containing:
        - number of successfully indexed documents
        - list of failed operations
    """
    if queryset is None:
        queryset = get_question_queryset()

    client = get_elasticsearch_client()

    success_count, errors = bulk(
        client,
        generate_question_bulk_actions(queryset),
        refresh=refresh,
        raise_on_error=False,
        raise_on_exception=False,
    )

    return success_count, errors


def get_user_queryset():
    """
    Return users with profile data loaded efficiently.
    """
    return User.objects.select_related("profile").order_by("pk")


def index_user(
    user,
    *,
    refresh: bool | str = False,
) -> dict[str, Any]:
    """
    Create or replace one user document in Elasticsearch.
    """
    client = get_elasticsearch_client()

    response = client.index(
        index=settings.ELASTICSEARCH_USER_INDEX,
        id=str(user.pk),
        document=user_to_document(user),
        refresh=refresh,
    )

    return dict(response)


def delete_user_document(
    user_id: int,
    *,
    refresh: bool | str = False,
) -> bool:
    """
    Delete one user document from Elasticsearch.
    """
    client = get_elasticsearch_client()

    try:
        client.delete(
            index=settings.ELASTICSEARCH_USER_INDEX,
            id=str(user_id),
            refresh=refresh,
        )
    except NotFoundError:
        return False

    return True


def generate_user_bulk_actions(queryset):
    """
    Yield Elasticsearch bulk actions for users.
    """
    index_name = settings.ELASTICSEARCH_USER_INDEX

    for user in queryset.iterator(chunk_size=500):
        yield {
            "_op_type": "index",
            "_index": index_name,
            "_id": str(user.pk),
            "_source": user_to_document(user),
        }


def bulk_index_users(
    queryset=None,
    *,
    refresh: bool | str = False,
) -> tuple[int, list]:
    """
    Bulk-index users into Elasticsearch.
    """
    if queryset is None:
        queryset = get_user_queryset()

    client = get_elasticsearch_client()

    success_count, errors = bulk(
        client,
        generate_user_bulk_actions(queryset),
        refresh=refresh,
        raise_on_error=False,
        raise_on_exception=False,
    )

    return success_count, errors


def get_topic_queryset():
    """
    Return all searchable topics.
    """
    return Topic.objects.order_by("pk")


def index_topic(
    topic: Topic,
    *,
    refresh: bool | str = False,
) -> dict[str, Any]:
    """
    Create or replace one topic document in Elasticsearch.
    """
    client = get_elasticsearch_client()

    response = client.index(
        index=settings.ELASTICSEARCH_TOPIC_INDEX,
        id=str(topic.pk),
        document=topic_to_document(topic),
        refresh=refresh,
    )

    return dict(response)


def delete_topic_document(
    topic_id: int,
    *,
    refresh: bool | str = False,
) -> bool:
    """
    Delete one topic document from Elasticsearch.
    """
    client = get_elasticsearch_client()

    try:
        client.delete(
            index=settings.ELASTICSEARCH_TOPIC_INDEX,
            id=str(topic_id),
            refresh=refresh,
        )
    except NotFoundError:
        return False

    return True


def generate_topic_bulk_actions(queryset):
    """
    Yield Elasticsearch bulk actions for topics.
    """
    index_name = settings.ELASTICSEARCH_TOPIC_INDEX

    for topic in queryset.iterator(chunk_size=500):
        yield {
            "_op_type": "index",
            "_index": index_name,
            "_id": str(topic.pk),
            "_source": topic_to_document(topic),
        }


def bulk_index_topics(
    queryset=None,
    *,
    refresh: bool | str = False,
) -> tuple[int, list]:
    """
    Bulk-index topics into Elasticsearch.
    """
    if queryset is None:
        queryset = get_topic_queryset()

    client = get_elasticsearch_client()

    success_count, errors = bulk(
        client,
        generate_topic_bulk_actions(queryset),
        refresh=refresh,
        raise_on_error=False,
        raise_on_exception=False,
    )

    return success_count, errors
