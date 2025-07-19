from django.urls import path

from decisions import views

app_name = "decisions"

urlpatterns = [
    path("", views.SearchView.as_view(), name="search"),
    path("results/", views.ResultsView.as_view(), name="results"),
    path("decision/<str:pk>/", views.DecisionView.as_view(), name="decision"),
]
