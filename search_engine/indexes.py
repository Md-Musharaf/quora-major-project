from django.conf import settings

from .client import get_elasticsearch_client

LOCAL_INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
}


QUESTION_INDEX_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "integer",
        },
        "title": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256,
                }
            },
        },
        "description": {
            "type": "text",
        },
        "topics": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                }
            },
        },
        "author_id": {
            "type": "integer",
        },
        "author_name": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256,
                }
            },
        },
        "created_at": {
            "type": "date",
        },
    },
}


USER_INDEX_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "integer",
        },
        "email": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256,
                }
            },
        },
        "display_name": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256,
                }
            },
        },
        "profession": {
            "type": "text",
        },
        "bio": {
            "type": "text",
        },
        "location": {
            "type": "text",
        },
    },
}


TOPIC_INDEX_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "integer",
        },
        "name": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256,
                }
            },
        },
        "description": {
            "type": "text",
        },
    },
}


def create_index(
    *,
    index_name: str,
    mappings: dict,
    recreate: bool = False,
) -> bool:
    """
    Create an Elasticsearch index.

    Returns True when created or recreated.
    Returns False when it already exists.
    """
    client = get_elasticsearch_client()

    index_exists = bool(client.indices.exists(index=index_name))

    if index_exists and not recreate:
        return False

    if index_exists:
        client.indices.delete(index=index_name)

    client.indices.create(
        index=index_name,
        settings=LOCAL_INDEX_SETTINGS,
        mappings=mappings,
    )

    return True


def create_question_index(
    *,
    recreate: bool = False,
) -> bool:
    return create_index(
        index_name=settings.ELASTICSEARCH_QUESTION_INDEX,
        mappings=QUESTION_INDEX_MAPPINGS,
        recreate=recreate,
    )


def create_user_index(
    *,
    recreate: bool = False,
) -> bool:
    return create_index(
        index_name=settings.ELASTICSEARCH_USER_INDEX,
        mappings=USER_INDEX_MAPPINGS,
        recreate=recreate,
    )


def create_topic_index(
    *,
    recreate: bool = False,
) -> bool:
    return create_index(
        index_name=settings.ELASTICSEARCH_TOPIC_INDEX,
        mappings=TOPIC_INDEX_MAPPINGS,
        recreate=recreate,
    )
