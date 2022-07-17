from django.urls import path

from portal.views import (
    GetHome,
    GetHomeFiltered,
    GetRollingStock,
    GetConsist,
    Consists,
    Companies,
    Scales,
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
    path("consists", Consists.as_view(), name="consists"),
    path(
        "consists/<int:page>", Consists.as_view(), name="consists_pagination"
    ),
    path("consist/<uuid:uuid>", GetConsist.as_view(), name="consist"),
    path(
        "consist/<uuid:uuid>/<int:page>",
        GetConsist.as_view(),
        name="consist_pagination",
    ),
    path("companies", Companies.as_view(), name="companies"),
    path(
        "companies/<int:page>",
        Companies.as_view(),
        name="companies_pagination"
    ),
    path("scales", Scales.as_view(), name="scales"),
    path(
        "scales/<int:page>",
        Scales.as_view(),
        name="scales_pagination"
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
