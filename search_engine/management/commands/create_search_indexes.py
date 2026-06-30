from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from search_engine.client import get_elasticsearch_client
from search_engine.indexes import (
    create_question_index,
    create_topic_index,
    create_user_index,
)


class Command(BaseCommand):
    help = "Create Elasticsearch indexes used by the project."

    def add_arguments(self, parser):
        parser.add_argument(
            "--recreate",
            action="store_true",
            help=(
                "Delete existing indexes and create them again. "
                "Existing indexed documents will be lost."
            ),
        )

    def handle(self, *args, **options):
        if not settings.ELASTICSEARCH_ENABLED:
            raise CommandError("Elasticsearch is disabled in Django settings.")

        client = get_elasticsearch_client()

        if not client.ping():
            raise CommandError("Could not connect to Elasticsearch.")

        recreate = options["recreate"]

        index_creators = [
            (
                "Question",
                create_question_index,
            ),
            (
                "User",
                create_user_index,
            ),
            (
                "Topic",
                create_topic_index,
            ),
        ]

        for index_label, create_function in index_creators:
            try:
                created = create_function(
                    recreate=recreate,
                )
            except Exception as exc:
                raise CommandError(
                    f"Could not create {index_label.lower()} " f"index: {exc}"
                ) from exc

            if created:
                action = "recreated" if recreate else "created"

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{index_label} index successfully " f"{action}."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{index_label} index already exists.")
                )
