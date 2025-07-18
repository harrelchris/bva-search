from django.contrib import admin

from tasks.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "datetime",
        "status",
    ]
    list_filter = [
        "name",
        "datetime",
        "status",
    ]


admin.site.register(Task, TaskAdmin)
