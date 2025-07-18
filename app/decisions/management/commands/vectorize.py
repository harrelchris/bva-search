from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "vectorize"


class Command(BaseCommand):
    help = "Populate the search_vector field for full-text search"

    def handle(self, *args, **options):
        queryset = Decision.objects.filter(text__isnull=False, search_vector__isnull=True)
        count = queryset.update(search_vector=SearchVector("text"))

        result = f"{count} decisions vectorized."
        Task.objects.create(
            name=TASK_NAME,
            status=True,
            description=result,
        )
        self.stdout.write(self.style.SUCCESS(result))
