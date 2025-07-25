import datetime
import urllib.parse

from django.core.management.base import BaseCommand

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "dates"
DEFAULT_DATE = datetime.date(year=1970, month=1, day=1)


class Command(BaseCommand):
    help = "Extract date from text, url, or use default date of 1970/01/01"

    def handle(self, *args, **options):
        query_set = Decision.objects.filter(date__isnull=True)

        decisions = []
        for decision in query_set:
            if not decision.text:
                continue
            elif decision.text.startswith("<"):
                # HTML error response. Clear to request text again.
                decision.text = None
                decision.search_vector = None
                decision.save()
                continue
            else:
                date = extract_text_date(decision.text) or extract_url_date(decision.url) or DEFAULT_DATE
                decision.date = date
                decisions.append(decision)

        Decision.objects.bulk_update(decisions, ["date"])

        msg = f"Extracted {len(decisions)} dates"
        self.stdout.write(self.style.SUCCESS(msg))
        Task.objects.create(
            name=TASK_NAME,
            status=True,
            description=msg,
        )


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
