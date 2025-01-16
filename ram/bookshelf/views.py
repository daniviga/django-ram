from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.schemas.openapi import AutoSchema

from ram.views import CustomLimitOffsetPagination
from bookshelf.models import Book, Catalog
from bookshelf.serializers import BookSerializer, CatalogSerializer


class BookList(ListAPIView):
    serializer_class = BookSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Book.objects.get_published(self.request.user)


class BookGet(RetrieveAPIView):
    serializer_class = BookSerializer
    lookup_field = "uuid"
    schema = AutoSchema(operation_id_base="retrieveBookByUUID")

    def get_queryset(self):
        return Book.objects.get_published(self.request.user)


class CatalogList(ListAPIView):
    serializer_class = CatalogSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Catalog.objects.get_published(self.request.user)


class CatalogGet(RetrieveAPIView):
    serializer_class = CatalogSerializer
    lookup_field = "uuid"
    schema = AutoSchema(operation_id_base="retrieveCatalogByUUID")

    def get_queryset(self):
        return Book.objects.get_published(self.request.user)
