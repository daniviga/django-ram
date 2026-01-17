import os
import shutil
from urllib.parse import urlparse
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.dates import MONTHS
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

from ram.utils import DeduplicatedStorage
from ram.models import BaseModel, Image, PropertyInstance
from ram.managers import BookManager, CatalogManager, MagazineIssueManager
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
        choices=sorted(settings.LANGUAGES, key=lambda s: s[1]),
        default="en",
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
    tags = models.ManyToManyField(Tag, related_name="bookshelf", blank=True)

    def delete(self, *args, **kwargs):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "images", "books", str(self.uuid)
            ),
            ignore_errors=True,
        )
        super(BaseBook, self).delete(*args, **kwargs)


def book_image_upload(instance, filename):
    return os.path.join("images", "books", str(instance.book.uuid), filename)


def magazine_image_upload(instance, filename):
    return os.path.join("images", "magazines", str(instance.uuid), filename)


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

    objects = BookManager()

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
            "bookshelf_item", kwargs={"selector": "book", "uuid": self.uuid}
        )


class Catalog(BaseBook):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="catalogs",
    )
    years = models.CharField(max_length=12)
    scales = models.ManyToManyField(Scale, related_name="catalogs")

    objects = CatalogManager()

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
            "bookshelf_item", kwargs={"selector": "catalog", "uuid": self.uuid}
        )

    def get_scales(self):
        return "/".join([s.scale for s in self.scales.all()])

    get_scales.short_description = "Scales"


class Magazine(BaseModel):
    name = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    ISBN = models.CharField(max_length=17, blank=True)  # 13 + dashes
    image = models.ImageField(
        blank=True,
        upload_to=magazine_image_upload,
        storage=DeduplicatedStorage,
    )
    language = models.CharField(
        max_length=7,
        choices=sorted(settings.LANGUAGES, key=lambda s: s[1]),
        default="en",
    )
    tags = models.ManyToManyField(Tag, related_name="magazine", blank=True)

    def delete(self, *args, **kwargs):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "images", "magazines", str(self.uuid)
            ),
            ignore_errors=True,
        )
        super(Magazine, self).delete(*args, **kwargs)

    class Meta:
        ordering = [Lower("name")]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("magazine", kwargs={"uuid": self.uuid})

    def get_cover(self):
        if self.image:
            return self.image
        else:
            cover_issue = self.issue.filter(published=True).first()
            if cover_issue and cover_issue.image.exists():
                return cover_issue.image.first().image
        return None

    def website_short(self):
        if self.website:
            return urlparse(self.website).netloc.replace("www.", "")


class MagazineIssue(BaseBook):
    magazine = models.ForeignKey(
        Magazine, on_delete=models.CASCADE, related_name="issue"
    )
    issue_number = models.CharField(max_length=100)
    publication_month = models.SmallIntegerField(
        null=True, blank=True, choices=MONTHS.items()
    )

    objects = MagazineIssueManager()

    class Meta:
        unique_together = ("magazine", "issue_number")
        ordering = [
            "magazine",
            "publication_year",
            "publication_month",
            "issue_number",
        ]

    def __str__(self):
        return f"{self.magazine.name} - {self.issue_number}"

    def clean(self):
        if self.magazine.published is False and self.published is True:
            raise ValidationError(
                "Cannot set an issue as published if the magazine is not "
                "published."
            )

    @property
    def obj_label(self):
        return "Magazine Issue"

    def preview(self):
        return self.image.first().image_thumbnail(100)

    @property
    def publisher(self):
        return self.magazine.publisher

    def get_absolute_url(self):
        return reverse(
            "issue", kwargs={"uuid": self.uuid, "magazine": self.magazine.uuid}
        )


class TocEntry(BaseModel):
    book = models.ForeignKey(
        BaseBook, on_delete=models.CASCADE, related_name="toc"
    )
    title = models.CharField()
    subtitle = models.CharField(blank=True)
    authors = models.CharField(blank=True)
    page = models.SmallIntegerField()
    featured = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["page"]
        verbose_name = "Table of Contents Entry"
        verbose_name_plural = "Table of Contents Entries"

    def __str__(self):
        if self.subtitle:
            title = f"{self.title}: {self.subtitle}"
        else:
            title = self.title
        return f"{title} (p. {self.page})"

    def clean(self):
        if self.page is None:
            raise ValidationError("Page number is required.")
        if self.page < 1:
            raise ValidationError("Page number is invalid.")
        try:
            if self.page > self.book.number_of_pages:
                raise ValidationError(
                    "Page number exceeds the publication's number of pages."
                )
        except TypeError:
            pass  # number_of_pages is None
