from django.contrib import admin

from decisions.models import Decision


class DecisionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "url",
        "lastmod",
    ]


admin.site.register(Decision, DecisionAdmin)
