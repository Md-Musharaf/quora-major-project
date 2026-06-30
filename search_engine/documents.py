from django.contrib.auth import get_user_model

from questions.models import Question
from topics.models import Topic

User = get_user_model()


def get_user_profile(user):
    """
    Return the user's profile when it exists.
    """
    return getattr(user, "profile", None)


def get_question_author_name(question: Question) -> str:
    """
    Return the question author's display name.

    Fall back to the user's email when no display name exists.
    """
    profile = get_user_profile(question.author)

    if profile:
        display_name = getattr(profile, "display_name", "")

        if display_name:
            return display_name.strip()

    return question.author.email


def question_to_document(question: Question) -> dict:
    """
    Convert a Django Question object into an Elasticsearch document.
    """
    return {
        "id": question.pk,
        "title": question.title or "",
        "description": question.description or "",
        "topics": list(question.topics.values_list("name", flat=True)),
        "author_id": question.author_id,
        "author_name": get_question_author_name(question),
        "created_at": question.created_at.isoformat(),
    }


def user_to_document(user: User) -> dict:
    """
    Convert a Django User object into an Elasticsearch document.
    """
    profile = get_user_profile(user)

    display_name = ""
    profession = ""
    bio = ""
    location = ""

    if profile:
        display_name = (getattr(profile, "display_name", "") or "").strip()

        profession = (getattr(profile, "profession", "") or "").strip()

        bio = (getattr(profile, "bio", "") or "").strip()

        location = (getattr(profile, "location", "") or "").strip()

    if not display_name:
        display_name = user.email

    return {
        "id": user.pk,
        "email": user.email or "",
        "display_name": display_name,
        "profession": profession,
        "bio": bio,
        "location": location,
    }


def topic_to_document(topic: Topic) -> dict:
    """
    Convert a Django Topic object into an Elasticsearch document.
    """
    return {
        "id": topic.pk,
        "name": topic.name or "",
        "description": topic.description or "",
    }
