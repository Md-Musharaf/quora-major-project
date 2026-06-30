import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
)
from django.dispatch import receiver

from questions.models import Question
from topics.models import Topic
from users.models import Profile

from .services import (
    delete_question_document,
    delete_topic_document,
    delete_user_document,
    get_question_queryset,
    get_topic_queryset,
    get_user_queryset,
    index_question,
    index_topic,
    index_user,
)

logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# Safe Elasticsearch operations
# ============================================================


def index_question_safely(question_id: int) -> None:
    """
    Fetch and index the latest committed question.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        question = get_question_queryset().get(pk=question_id)
    except Question.DoesNotExist:
        return

    try:
        index_question(question)
    except Exception:
        logger.exception(
            "Failed to index question %s.",
            question_id,
        )


def delete_question_safely(question_id: int) -> None:
    """
    Delete a question document without breaking the database action.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        delete_question_document(question_id)
    except Exception:
        logger.exception(
            "Failed to delete question %s.",
            question_id,
        )


def index_user_safely(user_id: int) -> None:
    """
    Fetch and index the latest committed user and profile data.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        user = get_user_queryset().get(pk=user_id)
    except User.DoesNotExist:
        return

    try:
        index_user(user)
    except Exception:
        logger.exception(
            "Failed to index user %s.",
            user_id,
        )


def delete_user_safely(user_id: int) -> None:
    """
    Delete a user document from Elasticsearch.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        delete_user_document(user_id)
    except Exception:
        logger.exception(
            "Failed to delete user %s.",
            user_id,
        )


def index_topic_safely(topic_id: int) -> None:
    """
    Fetch and index the latest committed topic.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        topic = get_topic_queryset().get(pk=topic_id)
    except Topic.DoesNotExist:
        return

    try:
        index_topic(topic)
    except Exception:
        logger.exception(
            "Failed to index topic %s.",
            topic_id,
        )


def delete_topic_safely(topic_id: int) -> None:
    """
    Delete a topic document from Elasticsearch.
    """
    if not settings.ELASTICSEARCH_ENABLED:
        return

    try:
        delete_topic_document(topic_id)
    except Exception:
        logger.exception(
            "Failed to delete topic %s.",
            topic_id,
        )


# ============================================================
# Transaction scheduling helpers
# ============================================================


def schedule_question_index(
    question_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: index_question_safely(question_id),
        using=using,
    )


def schedule_question_delete(
    question_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: delete_question_safely(question_id),
        using=using,
    )


def schedule_user_index(
    user_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: index_user_safely(user_id),
        using=using,
    )


def schedule_user_delete(
    user_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: delete_user_safely(user_id),
        using=using,
    )


def schedule_topic_index(
    topic_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: index_topic_safely(topic_id),
        using=using,
    )


def schedule_topic_delete(
    topic_id: int,
    *,
    using: str,
) -> None:
    transaction.on_commit(
        lambda: delete_topic_safely(topic_id),
        using=using,
    )


def schedule_multiple_question_indexes(
    question_ids,
    *,
    using: str,
) -> None:
    """
    Schedule multiple question documents for reindexing.
    """
    for question_id in set(question_ids):
        schedule_question_index(
            question_id,
            using=using,
        )


# ============================================================
# Question synchronization
# ============================================================


@receiver(
    post_save,
    sender=Question,
    dispatch_uid="search_engine_question_post_save",
)
def sync_question_after_save(
    sender,
    instance,
    raw,
    using,
    **kwargs,
):
    if raw:
        return

    schedule_question_index(
        instance.pk,
        using=using,
    )


@receiver(
    post_delete,
    sender=Question,
    dispatch_uid="search_engine_question_post_delete",
)
def remove_question_after_delete(
    sender,
    instance,
    using,
    **kwargs,
):
    schedule_question_delete(
        instance.pk,
        using=using,
    )


@receiver(
    m2m_changed,
    sender=Question.topics.through,
    dispatch_uid="search_engine_question_topics_changed",
)
def sync_question_after_topic_change(
    sender,
    instance,
    action,
    reverse,
    pk_set,
    using,
    **kwargs,
):
    if action not in {
        "post_add",
        "post_remove",
        "post_clear",
    }:
        return

    if not reverse:
        schedule_question_index(
            instance.pk,
            using=using,
        )
        return

    if pk_set:
        schedule_multiple_question_indexes(
            pk_set,
            using=using,
        )


# ============================================================
# User synchronization
# ============================================================


@receiver(
    post_save,
    sender=User,
    dispatch_uid="search_engine_user_post_save",
)
def sync_user_after_save(
    sender,
    instance,
    raw,
    using,
    **kwargs,
):
    if raw:
        return

    schedule_user_index(
        instance.pk,
        using=using,
    )


@receiver(
    post_delete,
    sender=User,
    dispatch_uid="search_engine_user_post_delete",
)
def remove_user_after_delete(
    sender,
    instance,
    using,
    **kwargs,
):
    schedule_user_delete(
        instance.pk,
        using=using,
    )


# ============================================================
# Profile synchronization
# ============================================================


@receiver(
    post_save,
    sender=Profile,
    dispatch_uid="search_engine_profile_post_save",
)
def sync_profile_after_save(
    sender,
    instance,
    raw,
    using,
    **kwargs,
):
    """
    Update the user document and questions containing author_name.
    """
    if raw:
        return

    user_id = instance.user_id

    schedule_user_index(
        user_id,
        using=using,
    )

    question_ids = Question.objects.filter(
        author_id=user_id,
    ).values_list(
        "pk",
        flat=True,
    )

    schedule_multiple_question_indexes(
        question_ids,
        using=using,
    )


@receiver(
    post_delete,
    sender=Profile,
    dispatch_uid="search_engine_profile_post_delete",
)
def sync_after_profile_delete(
    sender,
    instance,
    using,
    **kwargs,
):
    """
    Reindex using email as the display-name fallback.
    """
    user_id = instance.user_id

    schedule_user_index(
        user_id,
        using=using,
    )

    question_ids = Question.objects.filter(
        author_id=user_id,
    ).values_list(
        "pk",
        flat=True,
    )

    schedule_multiple_question_indexes(
        question_ids,
        using=using,
    )


# ============================================================
# Topic synchronization
# ============================================================


@receiver(
    post_save,
    sender=Topic,
    dispatch_uid="search_engine_topic_post_save",
)
def sync_topic_after_save(
    sender,
    instance,
    raw,
    using,
    **kwargs,
):
    """
    Update the topic document and every question using the topic.
    """
    if raw:
        return

    schedule_topic_index(
        instance.pk,
        using=using,
    )

    question_ids = Question.objects.filter(
        topics=instance,
    ).values_list(
        "pk",
        flat=True,
    )

    schedule_multiple_question_indexes(
        question_ids,
        using=using,
    )


@receiver(
    pre_delete,
    sender=Topic,
    dispatch_uid="search_engine_topic_pre_delete",
)
def remember_topic_questions_before_delete(
    sender,
    instance,
    using,
    **kwargs,
):
    """
    Store affected question IDs before the many-to-many rows disappear.
    """
    instance._search_question_ids = list(
        Question.objects.filter(
            topics=instance,
        ).values_list(
            "pk",
            flat=True,
        )
    )


@receiver(
    post_delete,
    sender=Topic,
    dispatch_uid="search_engine_topic_post_delete",
)
def remove_topic_after_delete(
    sender,
    instance,
    using,
    **kwargs,
):
    """
    Delete the topic document and refresh affected questions.
    """
    schedule_topic_delete(
        instance.pk,
        using=using,
    )

    question_ids = getattr(
        instance,
        "_search_question_ids",
        [],
    )

    schedule_multiple_question_indexes(
        question_ids,
        using=using,
    )
