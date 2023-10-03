from django.urls import path

from portal.views import (
    GetData,
    GetRoster,
    GetRosterFiltered,
    GetFlatpage,
    GetRollingStock,
    GetConsist,
    Consists,
    Companies,
    Manufacturers,
    Scales,
    Types,
    Books,
    GetBook,
    SearchRoster,
)

urlpatterns = [
    path("", GetData.as_view(), name="index"),
    path("roster", GetRoster.as_view(), name="roster"),
    path("roster/<int:page>", GetRoster.as_view(), name="roster_pagination"),
    path(
        "page/<str:flatpage>",
        GetFlatpage.as_view(),
        name="flatpage",
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
        name="companies_pagination",
    ),
    path(
        "manufacturers/<str:category>",
        Manufacturers.as_view(),
        name="manufacturers"
    ),
    path(
        "manufacturers/<str:category>/<int:page>",
        Manufacturers.as_view(),
        name="manufacturers_pagination",
    ),
    path("scales", Scales.as_view(), name="scales"),
    path("scales/<int:page>", Types.as_view(), name="scales_pagination"),
    path("types", Types.as_view(), name="types"),
    path("types/<int:page>", Types.as_view(), name="types_pagination"),
    path("bookshelf/books", Books.as_view(), name="books"),
    path("bookshelf/books/<int:page>", Books.as_view(), name="books_pagination"),
    path("bookshelf/book/<uuid:uuid>", GetBook.as_view(), name="book"),
    path(
        "search",
        SearchRoster.as_view(http_method_names=["post"]),
        name="search",
    ),
    path(
        "search/<str:search>/<int:page>",
        SearchRoster.as_view(),
        name="search_pagination",
    ),
    path(
        "<str:_filter>/<str:search>",
        GetRosterFiltered.as_view(),
        name="filtered",
    ),
    path(
        "<str:_filter>/<str:search>/<int:page>",
        GetRosterFiltered.as_view(),
        name="filtered_pagination",
    ),
    path("<uuid:uuid>", GetRollingStock.as_view(), name="rolling_stock"),
]
