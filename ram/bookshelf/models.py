from uuid import uuid4
from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField

from ckeditor_uploader.fields import RichTextUploadingField

from metadata.models import Tag
from ram.utils import DeduplicatedStorage
from ram.models import Image, PropertyInstance


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    country = CountryField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def short_name(self):
        return f"{self.last_name} {self.first_name[0]}."


class Book(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    ISBN = models.CharField(max_length=13, blank=True)
    language = models.CharField(
        max_length=7,
        choices=settings.LANGUAGES,
        default='en'
    )
    number_of_pages = models.SmallIntegerField(null=True, blank=True)
    publication_year = models.SmallIntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="bookshelf", blank=True
    )
    notes = RichTextUploadingField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def publisher_name(self):
        return self.publisher.name

    def get_absolute_url(self):
        return reverse("book", kwargs={"uuid": self.uuid})


class BookImage(Image):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="image"
    )
    image = models.ImageField(
        upload_to="images/books/",  # FIXME, find a better way to replace this
        storage=DeduplicatedStorage,
        null=True,
        blank=True
    )


class BookProperty(PropertyInstance):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="property",
    )
