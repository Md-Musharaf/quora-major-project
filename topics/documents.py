from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from core.elasticsearch import CompatibleDocument

from .models import Topic


@registry.register_document
class TopicDocument(CompatibleDocument):
    name = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )

    description = fields.TextField()

    slug = fields.KeywordField()

    class Index:
        name = "quora_topics"

        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Topic

        fields = [
            "id",
            "created_at",
            "updated_at",
        ]

        queryset_pagination = 500
