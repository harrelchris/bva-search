from django.contrib import admin

from decisions.models import Decision, Query


class DecisionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "url",
        "lastmod",
    ]


class QueryAdmin(admin.ModelAdmin):
    list_display = [
        "string",
        "created"
    ]

admin.site.register(Decision, DecisionAdmin)
admin.site.register(Query, QueryAdmin)
