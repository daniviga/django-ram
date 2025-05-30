import os
import shutil
from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField

from ram.utils import DeduplicatedStorage
from ram.models import BaseModel, Image, PropertyInstance
from metadata.models import Scale, Manufacturer, Shop, Tag


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

    @property
    def short_name(self):
        return f"{self.last_name} {self.first_name[0]}."


class BaseBook(BaseModel):
    ISBN = models.CharField(max_length=17, blank=True)  # 13 + dashes
    language = models.CharField(
        max_length=7,
        choices=settings.LANGUAGES,
        default='en'
    )
    number_of_pages = models.SmallIntegerField(null=True, blank=True)
    publication_year = models.SmallIntegerField(null=True, blank=True)
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, null=True, blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    purchase_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="bookshelf", blank=True
    )

    def delete(self, *args, **kwargs):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "images", "books", str(self.uuid)
            ),
            ignore_errors=True
        )
        super(BaseBook, self).delete(*args, **kwargs)


def book_image_upload(instance, filename):
    return os.path.join(
        "images",
        "books",
        str(instance.book.uuid),
        filename
    )


class BaseBookImage(Image):
    book = models.ForeignKey(
        BaseBook, on_delete=models.CASCADE, related_name="image"
    )
    image = models.ImageField(
        upload_to=book_image_upload,
        storage=DeduplicatedStorage,
    )


class BaseBookProperty(PropertyInstance):
    book = models.ForeignKey(
        BaseBook,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="property",
    )


class Book(BaseBook):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def publisher_name(self):
        return self.publisher.name

    @property
    def authors_list(self):
        return ", ".join(a.short_name for a in self.authors.all())

    def get_absolute_url(self):
        return reverse(
            "bookshelf_item",
            kwargs={"selector": "book", "uuid": self.uuid}
        )


class Catalog(BaseBook):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
    )
    years = models.CharField(max_length=12)
    scales = models.ManyToManyField(Scale)

    class Meta:
        ordering = ["manufacturer", "publication_year"]

    def __str__(self):
        # if the object is new, return an empty string to avoid
        # calling self.scales.all() which would raise a infinite recursion
        if self.pk is None:
            return str()  # empty string
        scales = self.get_scales()
        return "%s %s %s" % (self.manufacturer.name, self.years, scales)

    def get_absolute_url(self):
        return reverse(
            "bookshelf_item",
            kwargs={"selector": "catalog", "uuid": self.uuid}
        )

    def get_scales(self):
        return "/".join([s.scale for s in self.scales.all()])
    get_scales.short_description = "Scales"
