from django.urls import path
from bookshelf.views import BookList, BookGet, CatalogList, CatalogGet

urlpatterns = [
    path("book/list", BookList.as_view()),
    path("book/get/<uuid:uuid>", BookGet.as_view()),
    path("catalog/list", CatalogList.as_view()),
    path("catalog/get/<uuid:uuid>", CatalogGet.as_view()),
]
