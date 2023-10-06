from rest_framework import serializers
from bookshelf.models import Book, Author, Publisher
from metadata.serializers import TagSerializer


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
        fields = "__all__"
        read_only_fields = ("creation_time", "updated_time")
