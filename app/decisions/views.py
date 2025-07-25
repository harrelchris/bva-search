import datetime
import urllib.parse

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from django.views.generic import DetailView, ListView, TemplateView

from decisions.models import Decision, Query
from tasks.models import Task


class SearchView(TemplateView):
    template_name = "decisions/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["decision_count"] = Decision.objects.all().count()
        latest_datetime = Task.objects.filter(name="urls").order_by("-datetime").first()
        context["latest_date"] = latest_datetime.datetime.date().strftime("%x")
        return context


class ResultsView(ListView):
    model = Decision
    template_name = "decisions/results.html"
    paginate_by = 100

    def get(self, request, *args, **kwargs):
        q = self.request.GET.get("q", "").strip()
        if q:
            Query.objects.create(string=q)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return Decision.objects.none()

        today = datetime.date.today()
        start_date = datetime.date(year=today.year - 1, month=1, day=1)
        query = SearchQuery(q, search_type="websearch", config="english")
        query_set = Decision.objects.filter(search_vector=query)
        query_set = (
            query_set.annotate(
                rank=SearchRank(F("search_vector"), query),
                headline=SearchHeadline(
                    expression=F("text"),
                    query=query,
                    start_sel="<mark>",
                    stop_sel="</mark>",
                ),
            )
            .filter(
                date__range=(start_date, today),
            )
            .order_by("-rank")
            .values("pk", "headline", "date", "url")
        )
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        context["query"] = q
        context["query_url"] = urllib.parse.quote_plus(q)
        return context


class DecisionView(DetailView):
    model = Decision
    template_name = "decisions/decision.html"
