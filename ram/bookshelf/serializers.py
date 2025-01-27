from rest_framework import serializers
from bookshelf.models import Book, Catalog, Author, Publisher
from metadata.serializers import (
    ScaleSerializer,
    ManufacturerSerializer,
    TagSerializer
)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    publisher = PublisherSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Book
        exclude = (
            "notes",
            "shop",
            "purchase_date",
            "price",
        )
        read_only_fields = ("creation_time", "updated_time")


class CatalogSerializer(serializers.ModelSerializer):
    scales = ScaleSerializer(many=True)
    manufacturer = ManufacturerSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Catalog
        exclude = (
            "notes",
            "shop",
            "purchase_date",
            "price",
        )
        read_only_fields = ("creation_time", "updated_time")
