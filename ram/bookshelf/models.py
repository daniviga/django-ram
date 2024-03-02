import os
import shutil
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField

from tinymce import models as tinymce

from metadata.models import Tag
from ram.utils import DeduplicatedStorage
from ram.models import Image, PropertyInstance


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    country = CountryField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def short_name(self):
        return f"{self.last_name} {self.first_name[0]}."


class Book(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    ISBN = models.CharField(max_length=17, blank=True)  # 13 + dashes
    language = models.CharField(
        max_length=7,
        choices=settings.LANGUAGES,
        default='en'
    )
    number_of_pages = models.SmallIntegerField(null=True, blank=True)
    publication_year = models.SmallIntegerField(null=True, blank=True)
    description = tinymce.HTMLField(blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="bookshelf", blank=True
    )
    notes = tinymce.HTMLField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def publisher_name(self):
        return self.publisher.name

    def get_absolute_url(self):
        return reverse("book", kwargs={"uuid": self.uuid})

    def delete(self, *args, **kwargs):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "images", "books", str(self.uuid)
            ),
            ignore_errors=True
        )
        super(Book, self).delete(*args, **kwargs)


def book_image_upload(instance, filename):
    return os.path.join(
        "images",
        "books",
        str(instance.book.uuid),
        filename
    )


class BookImage(Image):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="image"
    )
    image = models.ImageField(
        upload_to=book_image_upload,
        storage=DeduplicatedStorage,
    )


class BookProperty(PropertyInstance):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="property",
    )
