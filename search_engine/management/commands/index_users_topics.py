from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from search_engine.client import get_elasticsearch_client
from search_engine.services import (
    bulk_index_topics,
    bulk_index_users,
    get_topic_queryset,
    get_user_queryset,
)


class Command(BaseCommand):
    help = "Index existing users and topics in Elasticsearch."

    def handle(self, *args, **options):
        if not settings.ELASTICSEARCH_ENABLED:
            raise CommandError("Elasticsearch is disabled in Django settings.")

        client = get_elasticsearch_client()

        if not client.ping():
            raise CommandError("Could not connect to Elasticsearch.")

        required_indexes = [
            settings.ELASTICSEARCH_USER_INDEX,
            settings.ELASTICSEARCH_TOPIC_INDEX,
        ]

        for index_name in required_indexes:
            if not client.indices.exists(index=index_name):
                raise CommandError(
                    f'Elasticsearch index "{index_name}" '
                    "does not exist. Run "
                    "python manage.py create_search_indexes first."
                )

        self.index_users()
        self.index_topics()

    def index_users(self):
        queryset = get_user_queryset()
        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("There are no users to index."))
            return

        self.stdout.write(f"Indexing {total} user(s)...")

        try:
            success_count, errors = bulk_index_users(
                queryset,
                refresh="wait_for",
            )
        except Exception as exc:
            raise CommandError(f"User indexing failed: {exc}") from exc

        if errors:
            self.stdout.write(
                self.style.WARNING(f"{len(errors)} user(s) failed to index.")
            )

            for error in errors[:5]:
                self.stderr.write(str(error))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {success_count} " "user(s).")
        )

    def index_topics(self):
        queryset = get_topic_queryset()
        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("There are no topics to index."))
            return

        self.stdout.write(f"Indexing {total} topic(s)...")

        try:
            success_count, errors = bulk_index_topics(
                queryset,
                refresh="wait_for",
            )
        except Exception as exc:
            raise CommandError(f"Topic indexing failed: {exc}") from exc

        if errors:
            self.stdout.write(
                self.style.WARNING(f"{len(errors)} topic(s) failed to index.")
            )

            for error in errors[:5]:
                self.stderr.write(str(error))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {success_count} " "topic(s).")
        )
