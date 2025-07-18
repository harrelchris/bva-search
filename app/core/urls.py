from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults

admin.site.index_title = admin.site.name = admin.site.site_header = admin.site.site_title = "BVA Search Admin"

urlpatterns = [
    path("", include("decisions.urls"), name="decisions"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
    urlpatterns.extend(
        [
            path(
                "400/",
                defaults.bad_request,
                kwargs={"exception": Exception("Bad Request")},
            ),
            path(
                "403/",
                defaults.permission_denied,
                kwargs={"exception": Exception("Permission Denied")},
            ),
            path(
                "404/",
                defaults.page_not_found,
                kwargs={"exception": Exception("Not Found")},
            ),
            path("500/", defaults.server_error),
        ],
    )
