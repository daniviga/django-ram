from django.urls import path
from bookshelf.views import BookList, BookGet

urlpatterns = [
    path("book/list", BookList.as_view()),
    path("book/get/<uuid:uuid>", BookGet.as_view()),
]
