from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Profile, User

@registry.register_document
class UserDocument(Document):
    email = fields.KeywordField()

    display_name = fields.TextField(
        attr="profile.display_name",
        fields={
            "raw": fields.KeywordField(),
        },
    )

    bio = fields.TextField(
        attr="profile.bio",
    )

    profession = fields.TextField(
        attr="profile.profession",
    )

    location = fields.TextField(
        attr="profile.location",
    )

    class Index:
        name = "quora_users"

        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = User

        fields = [
            "id",
            "date_joined",
        ]

        related_models = [
            Profile,
        ]

        queryset_pagination = 500

    def get_queryset(self):
        return super().get_queryset().select_related("profile")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Profile):
            return related_instance.user

        return None
