from django.contrib import admin

from index.models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "created",
    ]


admin.site.register(Contact, ContactAdmin)
