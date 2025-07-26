import unicodedata
from concurrent.futures import Future, as_completed

from django.core.management.base import BaseCommand
from django.db import DataError
from django.db.models import QuerySet
from requests_futures.sessions import FuturesSession

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "text"
BATCH_SIZE = 100

session = FuturesSession()


class Command(BaseCommand):
    help = "Fetch text for urls from BVA server"

    def handle(self, *args, **options):
        query_set = get_query_set()
        discovered = query_set.count()

        if not discovered:
            self.record_success(f"{discovered} new decisions")
            return

        updated_objects = 0
        query_set_chunks = chunk_queryset(qs=query_set, n=BATCH_SIZE)
        for query_set_chunk in query_set_chunks:
            futures = create_futures(query_set_chunk)
            responses = request_futures(futures)
            decisions = modify_decisions(responses)
            count = self.save_decisions(decisions)
            updated_objects += count

        self.record_success(f"{updated_objects} decisions updated")

    def record_success(self, msg: str):
        self.stdout.write(self.style.SUCCESS(msg))
        Task.objects.create(
            name=TASK_NAME,
            status=True,
            description=msg,
        )

    def record_error(self, msg: str):
        self.stdout.write(self.style.ERROR(msg))
        Task.objects.create(
            name=TASK_NAME,
            status=False,
            description=msg,
        )

    def save_decisions(self, decisions: list[Decision]) -> int:
        try:
            updated_objects = Decision.objects.bulk_update(decisions, ["text"])
        except DataError:
            updated_objects = 0
            for decision in decisions:
                cleaned_text = clean_null_bytes(decision.text)
                decision.text = cleaned_text
                try:
                    decision.save()
                except DataError:
                    self.record_error(f"Error fetching text: {decision.pk} - {decision.url}")
                    continue
                else:
                    updated_objects += 1
            return updated_objects
        else:
            return updated_objects


def get_query_set():
    return Decision.objects.filter(text__isnull=True).values_list("pk", "url")


def chunk_queryset(qs: QuerySet, n: int):
    total = qs.count()
    for start in range(0, total, n):
        yield qs[start : start + n]


def create_futures(query_set: QuerySet) -> list[Future]:
    futures = []
    for pk, url in query_set:
        future = session.get(url)
        future.pk = pk
        futures.append(future)
    return futures


def request_futures(futures: list[Future]):
    responses = []
    for future in as_completed(futures):
        response = future.result()
        response.pk = future.pk  # noqa
        responses.append(response)
    return responses


def modify_decisions(responses: list) -> list[Decision]:
    decisions = []
    for response in responses:
        decision = Decision.objects.get(pk=response.pk)
        decision.text = response.text
        decisions.append(decision)
    return decisions


def clean_null_bytes(text: str) -> str:
    """Remove null characters and normalize unicode"""

    text = text.replace("\x00", "")
    text = text.replace("\ufeff", "")
    text = unicodedata.normalize("NFKC", text)
    return text
