import datetime
import urllib.parse

from django.core.management.base import BaseCommand
from django.db import DataError

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "dates"
DEFAULT_DATE = datetime.date(year=1970, month=1, day=1)


class Command(BaseCommand):
    help = "Extract date from text, url, or use default date of 1970/01/01"

    def handle(self, *args, **options):
        query_set = get_query_set()
        discovered = query_set.count()

        if not discovered:
            self.record_success(f"{discovered} new decisions")
            return

        decisions = []
        for decision in query_set:
            # HTML error page. Need to request again
            if decision.text.startswith("<"):
                reset_decision(decision)
                self.record_error(f"Error extracting date: {decision.pk} - {decision.url}")
                continue
            else:
                date = extract_text_date(decision.text) or extract_url_date(decision.url) or DEFAULT_DATE
                decision.date = date
                decisions.append(decision)
        self.save_decisions(decisions)
        self.record_success(f"{len(decisions)} objects updated")

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
            updated_objects = Decision.objects.bulk_update(decisions, ["date"])
        except DataError:
            for decision in decisions:
                try:
                    decision.save()
                except DataError:
                    self.record_error(f"Error saving date: {decision.pk} - {decision.url}")


def get_query_set():
    return Decision.objects.filter(text__isnull=False, date__isnull=True)


def reset_decision(decision: Decision):
    decision.text = None
    decision.search_vector = None
    decision.save()


def extract_text_date(text: str) -> datetime.date | None:
    for line in text.splitlines():
        if line.startswith("Decision Date"):
            return extract_decision_date(line)
    else:
        return None


def extract_decision_date(line: str):
    parts = line.split()

    # Decision Date: 01/06/23	Archive Date: 01/06/23
    try:
        date_str = parts[2]
        date_obj = datetime.datetime.strptime(date_str, "%m/%d/%y").date()
    except (ValueError, IndexError):
        pass
    else:
        return date_obj

    # Decision Date: 01/06/2023	Archive Date: 01/06/2023
    try:
        date_str = parts[2]
        date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    except (ValueError, IndexError):
        pass
    else:
        return date_obj

    # Decision Date: 	Archive Date: 03/28/18
    try:
        date_str = parts[4]
        date_obj = datetime.datetime.strptime(date_str, "%m/%d/%y").date()
    except (ValueError, IndexError):
        pass
    else:
        return date_obj

    # Decision Date: 	Archive Date: 03/28/2018
    try:
        date_str = parts[4]
        date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    except (ValueError, IndexError):
        pass
    else:
        return date_obj

    return DEFAULT_DATE


def extract_url_date(url: str) -> datetime.date | None:
    # http://www.va.gov/vetapp95/files3/9511339.txt

    if not "vetapp" in url:
        return None

    results = urllib.parse.urlparse(url=url)
    parts = results.path.split("/")
    year_str = parts[1].lstrip("vetapp")
    year = resolve_year(year_str)
    return datetime.date(year=year, month=1, day=1)


def resolve_year(year_str: str) -> int:
    # 92 to current year as 2 digits

    if int(year_str) < 92:
        year_st = "20" + year_str
    else:
        year_st = "19" + year_str
    return int(year_st)
