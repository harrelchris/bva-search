from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "vectors"


class Command(BaseCommand):
    help = "Populate the search_vector field for full-text search"

    def handle(self, *args, **options):
        self.stdout.write(f"Vectorizing decisions")
        queryset = Decision.objects.filter(text__isnull=False, search_vector__isnull=True)
        count = len(queryset)
        self.stdout.write(f"{count} decisions found")
        count = queryset.update(search_vector=SearchVector("text", config="english"))
        result = f"{count} decisions vectorized"
        Task.objects.create(
            name=TASK_NAME,
            status=True,
            description=result,
        )
        self.stdout.write(self.style.SUCCESS(result))
