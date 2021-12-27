"""dcc URL Configuration

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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from roster import urls as roster_urls
from driver import urls as driver_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('roster/', include(roster_urls)),
    path('dcc/', include(driver_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     from django.views.generic import TemplateView
#     from rest_framework.schemas import get_schema_view
# 
#     urlpatterns += [
#         path('swagger/', TemplateView.as_view(
#             template_name='swagger.html',
#             extra_context={'schema_url': 'openapi-schema'}
#         ), name='swagger'),
#         path('openapi', get_schema_view(
#             title="BITE - A Basic/IoT/Example",
#             description="BITE API for IoT",
#             version="1.0.0"
#         ), name='openapi-schema'),
#     ]
