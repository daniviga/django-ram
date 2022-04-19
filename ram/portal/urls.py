from django.urls import path

from portal.views import (
    GetHome,
    GetHomeFiltered,
    GetRollingStock,
    GetConsist,
    Consists,
)

urlpatterns = [
    path("", GetHome.as_view(), name="index"),
    path("<int:page>", GetHome.as_view(), name="index_pagination"),
    path(
        "search",
        GetHomeFiltered.as_view(http_method_names=["post"]),
        name="search",
    ),
    path("search/<str:search>", GetHomeFiltered.as_view(), name="search"),
    path(
        "search/<str:search>/<int:page>",
        GetHomeFiltered.as_view(),
        name="search_pagination",
    ),
    path("consist", Consists.as_view(), name="consists"),
    path("consist/<uuid:uuid>", GetConsist.as_view(), name="consist"),
    path(
        "consist/<uuid:uuid>/<int:page>",
        GetConsist.as_view(),
        name="consist_pagination",
    ),
    path(
        "<str:_filter>/<str:search>",
        GetHomeFiltered.as_view(),
        name="filtered",
    ),
    path(
        "<str:_filter>/<str:search>/<int:page>",
        GetHomeFiltered.as_view(),
        name="filtered_pagination",
    ),
    path("<uuid:uuid>", GetRollingStock.as_view(), name="rolling_stock"),
]
