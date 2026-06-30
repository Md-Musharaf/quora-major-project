from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from search_engine.client import get_elasticsearch_client
from search_engine.services import (
    bulk_index_questions,
    get_question_queryset,
)


class Command(BaseCommand):
    help = "Index all existing questions in Elasticsearch."

    def handle(self, *args, **options):
        if not settings.ELASTICSEARCH_ENABLED:
            raise CommandError("Elasticsearch is disabled in Django settings.")

        client = get_elasticsearch_client()
        index_name = settings.ELASTICSEARCH_QUESTION_INDEX

        if not client.ping():
            raise CommandError("Could not connect to Elasticsearch.")

        if not client.indices.exists(index=index_name):
            raise CommandError(
                f'Elasticsearch index "{index_name}" does not exist. '
                "Run python manage.py create_search_indexes first."
            )

        queryset = get_question_queryset()
        total_questions = queryset.count()

        if total_questions == 0:
            self.stdout.write(self.style.WARNING("There are no questions to index."))
            return

        self.stdout.write(f"Indexing {total_questions} question(s)...")

        try:
            success_count, errors = bulk_index_questions(
                queryset,
                refresh="wait_for",
            )
        except Exception as exc:
            raise CommandError(f"Question indexing failed: {exc}") from exc

        if errors:
            self.stdout.write(
                self.style.WARNING(f"{len(errors)} question(s) failed to index.")
            )

            for error in errors[:5]:
                self.stderr.write(str(error))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {success_count} " "question(s).")
        )
