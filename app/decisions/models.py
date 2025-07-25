from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class Decision(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    url = models.URLField(unique=True)
    lastmod = models.DateField()
    text = models.TextField(null=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]


class Query(models.Model):
    string = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Queries"
        ordering = ["-created"]
