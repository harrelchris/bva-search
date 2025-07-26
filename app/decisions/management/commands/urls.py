import bs4
import requests
from django.core.management.base import BaseCommand

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "urls"


class Command(BaseCommand):
    help = "Fetch urls from BVA sitemaps"

    def handle(self, *args, **options):
        created_objects = 0
        main_sitemap_soup = request_sitemap(url="https://www.va.gov/sitemap_bva.xml")

        if not main_sitemap_soup:
            self.record_error(f"Error requesting main sitemap: https://www.va.gov/sitemap_bva.xml")
            return

        sitemap_list = extract_annual_sitemaps(soup=main_sitemap_soup)
        last_run = get_last_run()
        filtered_sitemap_list = filter_list(elements=sitemap_list, last_run=last_run)

        for sitemap_dict in filtered_sitemap_list:
            self.stdout.write(f"Requesting {sitemap_dict['loc']}")
            annual_sitemap_soup = request_sitemap(url=sitemap_dict["loc"])
            if not annual_sitemap_soup:
                self.record_error(f"Error requesting annual sitemap: {sitemap_dict['loc']}")
                continue
            url_list = extract_sitemap_urls(soup=annual_sitemap_soup)
            filtered_url_list = filter_list(elements=url_list, last_run=last_run)
            decisions = create_decisions(urls=filtered_url_list)
            objects = Decision.objects.bulk_create(decisions, ignore_conflicts=True)
            created_objects += len(objects)

        self.record_success(f"{created_objects} decisions created")

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


def request_sitemap(url: str) -> bs4.BeautifulSoup | None:
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None
    return bs4.BeautifulSoup(response.content, "lxml-xml")


def extract_annual_sitemaps(soup: bs4.BeautifulSoup) -> list[dict[str, str]]:
    output = []
    sitemap_index = soup.find("sitemapindex")
    sitemap_elements = sitemap_index.find_all("sitemap")
    for sitemap_element in sitemap_elements:
        loc = sitemap_element.find("loc").text
        lastmod = sitemap_element.find("lastmod").text
        output.append(
            {
                "loc": loc,
                "lastmod": lastmod,
            }
        )
    return output


def get_last_run() -> str:
    task = Task.objects.filter(name=TASK_NAME, status=True).order_by("-datetime").first()
    if not task:
        return "1970-01-01"
    else:
        return task.datetime.date().strftime("%Y-%m-%d")


def filter_list(elements: list[dict[str, str]], last_run: str) -> list[dict[str, str]]:
    output = []
    for element in elements:
        if element["lastmod"] > last_run:
            output.append(element)
    return output


def extract_sitemap_urls(soup: bs4.BeautifulSoup) -> list[dict[str, str]]:
    output = []
    url_set = soup.find("urlset")
    url_elements = url_set.find_all("url")
    for url_element in url_elements:
        loc = url_element.find("loc").text
        lastmod = url_element.find("lastmod").text
        output.append(
            {
                "loc": loc,
                "lastmod": lastmod,
            }
        )
    return output


def create_decisions(urls: list[dict[str, str]]) -> list[Decision]:
    decisions = []
    for url in urls:
        # https://www.va.gov/vetapp25/Files5/A25048321.txt -> A25048321
        pk = url["loc"].split("/")[-1].split(".")[0]
        decision = Decision(
            id=pk,
            url=url["loc"],
            lastmod=url["lastmod"],
        )
        decisions.append(decision)
    return decisions
