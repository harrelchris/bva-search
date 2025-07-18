from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from decisions.models import Decision


class Command(BaseCommand):
    help = "Populate the search_vector field for full-text search"

    def handle(self, *args, **options):
        count = 0
        query_set = Decision.objects.filter(text__isnull=False, search_vector__isnull=True)
        for decision in query_set:
            annotated = Decision.objects.annotate(vector=SearchVector("text")).get(pk=decision.pk)
            decision.search_vector = annotated.vector
            decision.save(update_fields=["search_vector"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} decisions vectorized."))
