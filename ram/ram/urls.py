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
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", lambda r: redirect("portal/")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("portal/", include("portal.urls")),
    path("ht/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/consist/", include("consist.urls")),
    path("api/v1/roster/", include("roster.urls")),
    path("api/v1/dcc/", include("driver.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
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
