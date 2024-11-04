from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.schemas.openapi import AutoSchema

from bookshelf.models import Book
from bookshelf.serializers import BookSerializer


class BookList(ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.get_published(self.request.user)


class BookGet(RetrieveAPIView):
    serializer_class = BookSerializer
    lookup_field = "uuid"
    schema = AutoSchema(operation_id_base="retrieveBookByUUID")

    def get_queryset(self):
        return Book.objects.get_published(self.request.user)
