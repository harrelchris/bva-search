from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from django.views.generic import DetailView, ListView, TemplateView

from decisions.models import Decision


class SearchView(TemplateView):
    template_name = "decisions/search.html"


class ResultsView(ListView):
    model = Decision
    template_name = "decisions/results.html"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        query = SearchQuery(
            value=q,
            search_type="websearch",
        )
        headline = SearchHeadline(
            expression=F("text"),
            query=query,
            start_sel="<mark>",
            stop_sel="</mark>",
        )
        return (
            Decision.objects.annotate(rank=SearchRank(F("search_vector"), query))
            .annotate(headline=headline)
            .filter(rank__gte=0.001)
            .order_by("-rank")
        )


class DecisionView(DetailView):
    model = Decision
    template_name = "decisions/decision.html"
