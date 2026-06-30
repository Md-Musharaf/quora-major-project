from functools import lru_cache

from django.conf import settings
from elasticsearch import Elasticsearch


@lru_cache(maxsize=1)
def get_elasticsearch_client() -> Elasticsearch:
    """
    Return a reusable Elasticsearch client instance.
    """
    return Elasticsearch(
        settings.ELASTICSEARCH_URL,
        request_timeout=10,
    )
