from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from topics.models import Topic
from users.models import Profile, User

from .models import Question


@registry.register_document
class QuestionDocument(Document):
    title = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )

    description = fields.TextField()

    author = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "email": fields.KeywordField(),
            "display_name": fields.TextField(
                attr="profile.display_name",
                fields={
                    "raw": fields.KeywordField(),
                },
            ),
            "profession": fields.TextField(
                attr="profile.profession",
            ),
        }
    )

    topics = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(
                fields={
                    "raw": fields.KeywordField(),
                }
            ),
            "slug": fields.KeywordField(),
        }
    )

    class Index:
        name = "quora_questions"

        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Question

        fields = [
            "id",
            "created_at",
            "updated_at",
        ]

        related_models = [
            User,
            Profile,
            Topic,
        ]

        queryset_pagination = 500

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("author__profile")
            .prefetch_related("topics")
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.questions.all()

        if isinstance(related_instance, Profile):
            return related_instance.user.questions.all()

        if isinstance(related_instance, Topic):
            return related_instance.questions.all()

        return Question.objects.none()
