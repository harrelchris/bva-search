from concurrent.futures import as_completed

from django.core.management.base import BaseCommand
from requests_futures.sessions import FuturesSession

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "text"
BATCH_SIZE = 100
session = FuturesSession()


class Command(BaseCommand):
    help = "Fetch text for urls from BVA server"

    def handle(self, *args, **options):
        while True:
            query_set = Decision.objects.filter(text__isnull=True).values_list("pk", "url")[:BATCH_SIZE]
            if not query_set:
                break

            futures = []
            for pk, url in query_set:
                future = session.get(url)
                future.pk = pk
                futures.append(future)

            decisions = []
            for future in as_completed(futures):
                response = future.result()
                decision = Decision.objects.get(pk=future.pk)
                decision.text = response.text
                decisions.append(decision)

            Decision.objects.bulk_update(decisions, ["text"])
            self.stdout.write(self.style.SUCCESS(f"Fetched {BATCH_SIZE} decisions: {decisions[0].pk} - {decisions[-1].pk}"))

        Task.objects.create(
            name=TASK_NAME,
            status=True,
        )
