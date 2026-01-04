"""ram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ram.views import UploadImage, DownloadFile
from portal.views import Render404

handler404 = Render404.as_view()

urlpatterns = [
    path("", lambda r: redirect("portal/")),
    path("tinymce/", include("tinymce.urls")),
    path("tinymce/upload_image", UploadImage.as_view(), name="upload_image"),
    path("portal/", include("portal.urls")),
    path("admin/", admin.site.urls),
    path("media/files/<path:filename>", DownloadFile.as_view(), name="download_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Enable the "/dcc" routing only if the "driver" app is active
if apps.is_installed("driver"):
    urlpatterns += [
        path("api/v1/dcc/", include("driver.urls")),
    ]

if settings.REST_ENABLED:
    urlpatterns += [
        path("api/v1/consist/", include("consist.urls")),
        path("api/v1/roster/", include("roster.urls")),
        path("api/v1/bookshelf/", include("bookshelf.urls")),
    ]

if settings.DEBUG:
    if apps.is_installed("debug_toolbar"):
        urlpatterns += [
            path("__debug__/", include("debug_toolbar.urls")),
        ]
    if settings.REST_ENABLED:
        from django.views.generic import TemplateView
        from rest_framework.schemas import get_schema_view
        urlpatterns += [
            path(
                "swagger/",
                TemplateView.as_view(
                    template_name="swagger.html",
                    extra_context={"schema_url": "openapi-schema"},
                ),
                name="swagger",
            ),
            path(
                "openapi",
                get_schema_view(
                    title="RAM - Railroad Assets Manager",
                    description="RAM API",
                    version="1.0.0",
                ),
                name="openapi-schema",
            ),
        ]
