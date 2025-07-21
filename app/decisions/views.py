import urllib.parse

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from django.views.generic import DetailView, ListView, TemplateView

from decisions.models import Decision


class SearchView(TemplateView):
    template_name = "decisions/search.html"


class ResultsView(ListView):
    model = Decision
    template_name = "decisions/results.html"
    paginate_by = 100

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        if not q:
            return Decision.objects.none()

        query = SearchQuery(q, search_type="websearch")
        query_set = Decision.objects.filter(search_vector=query)
        query_set = query_set.annotate(
            rank=SearchRank(F("search_vector"), query),
            headline=SearchHeadline(
                expression=F("text"),
                query=query,
                start_sel="<mark>",
                stop_sel="</mark>",
            )
        ).filter(
            rank__gte=0.02
        ).order_by("-rank").values("pk", "headline", "rank")
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "")
        context["query"] = urllib.parse.quote_plus(query)
        return context


class DecisionView(DetailView):
    model = Decision
    template_name = "decisions/decision.html"
