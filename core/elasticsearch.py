from django_elasticsearch_dsl import Document


class CompatibleDocument(Document):
    """
    Compatibility fix for django-elasticsearch-dsl 9.0.

    Ensures internal preparation attributes are stored directly
    on the document instance instead of inside Elasticsearch
    document data.
    """

    def __init__(self, related_instance_to_ignore=None, **kwargs):
        super().__init__(
            related_instance_to_ignore=related_instance_to_ignore,
            **kwargs,
        )

        object.__setattr__(
            self,
            "_related_instance_to_ignore",
            related_instance_to_ignore,
        )

        object.__setattr__(
            self,
            "_prepared_fields",
            self.init_prepare(),
        )
