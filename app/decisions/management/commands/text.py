import unicodedata
from concurrent.futures import as_completed

from django.core.management.base import BaseCommand
from django.db.utils import DataError
from requests_futures.sessions import FuturesSession

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "text"
BATCH_SIZE = 100
session = FuturesSession()


class Command(BaseCommand):
    help = "Fetch text for urls from BVA server"

    def handle(self, *args, **options):
        status = True
        description = None
        errors = 0
        while True:
            # Get all decision records with null text
            query_set = Decision.objects.filter(text__isnull=True).values_list("pk", "url")[:BATCH_SIZE]
            if not query_set:
                description = "No null text decisions"
                break

            # Request urls in batches
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

            # Try updating in bulk, then clean and retry individually
            try:
                Decision.objects.bulk_update(decisions, ["text"])
            except DataError:
                for decision in decisions:
                    try:
                        cleaned_text = clean_null_bytes(decision.text)
                        decision.text = cleaned_text
                        decision.save()
                    except DataError as e:
                        status = False
                        errors += 1
                        bad_chars = [c for c in decision.text if ord(c) < 32 and c not in "\n\r\t"]
                        msg = f"Error saving {decision.pk}: {e}. Problematic characters: {bad_chars}"
                        self.stdout.write(self.style.ERROR(msg))
            msg = f"Fetched {BATCH_SIZE} decisions: {decisions[0].pk} - {decisions[-1].pk}"
            self.stdout.write(self.style.SUCCESS(msg))

        if errors:
            description = f"{errors} errors"

        Task.objects.create(
            name=TASK_NAME,
            status=status,
            description=description,
        )


def clean_null_bytes(text: str) -> str:
    """Remove null characters and normalize unicode"""

    text = text.replace("\x00", "")
    text = text.replace("\ufeff", "")
    text = unicodedata.normalize("NFKC", text)
    return text
