from django.core.management.base import BaseCommand
import bs4
import requests

from decisions.models import Decision
from tasks.models import Task

TASK_NAME = "urls"


class Command(BaseCommand):
    help = "Fetch urls from BVA sitemaps"

    def handle(self, *args, **options):
        last_run = get_last_run()
        soup = request_sitemap(url="https://www.va.gov/sitemap_bva.xml")
        sitemap_index = soup.find("sitemapindex")
        sitemap_elements = sitemap_index.find_all("sitemap")
        for sitemap_element in sitemap_elements:
            loc = sitemap_element.find("loc").text
            lastmod = sitemap_element.find("lastmod").text
            if lastmod < last_run:
                continue
            self.stdout.write(f"Requesting sitemap: {loc}")
            soup = request_sitemap(url=loc)
            url_set = soup.find("urlset")
            url_elements = url_set.find_all("url")
            decisions = []
            for url_element in url_elements:
                loc = url_element.find("loc").text
                lastmod = url_element.find("lastmod").text
                id = loc.split("/")[-1].split(".")[0]
                decision = Decision(
                    id=id,
                    url=loc,
                    lastmod=lastmod,
                )
                decisions.append(decision)
            Decision.objects.bulk_create(
                objs=decisions,
                ignore_conflicts=True,
            )
        Task.objects.create(
            name=TASK_NAME,
            status=True,
        )


def get_last_run():
    task = Task.objects.filter(name=TASK_NAME).order_by("-datetime").first()
    if not task:
        return "1970-01-01"
    else:
        return task.datetime.date().strftime("%Y-%m-%d")


def request_sitemap(url: str) -> bs4.BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return bs4.BeautifulSoup(response.content, "lxml-xml")
