from django.urls import path

from portal.views import GetHome, GetHomeFiltered, GetRollingStock

urlpatterns = [
    path("", GetHome.as_view(), name="index"),
    path("<int:page>", GetHome.as_view(), name="index_pagination"),
    path(
        "search",
        GetHomeFiltered.as_view(http_method_names=["post"]),
        name="index_filtered",
    ),
    path(
        "search/<str:search>", GetHomeFiltered.as_view(), name="index_filtered"
    ),
    path(
        "search/<str:search>/<int:page>",
        GetHomeFiltered.as_view(),
        name="index_filtered_pagination",
    ),
    path("<uuid:uuid>", GetRollingStock.as_view(), name="rolling_stock"),
]
