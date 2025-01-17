import os
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

from ram.models import Document
from ram.utils import DeduplicatedStorage, get_image_preview, slugify
from ram.managers import PublicManager


class Property(models.Model):
    name = models.CharField(max_length=128, unique=True)
    private = models.BooleanField(
        default=False,
        help_text="Property will be only visible to logged users",
    )

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["name"]

    def __str__(self):
        return self.name

    objects = PublicManager()


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True, editable=False)
    category = models.CharField(
        max_length=64, choices=settings.MANUFACTURER_TYPES
    )
    website = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to=os.path.join("images", "manufacturers"),
        storage=DeduplicatedStorage,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered",
            kwargs={
                "_filter": "manufacturer",
                "search": self.slug,
            },
        )

    def logo_thumbnail(self):
        return get_image_preview(self.logo.url)

    logo_thumbnail.short_description = "Preview"


class Company(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=64, unique=True, editable=False)
    extended_name = models.CharField(max_length=128, blank=True)
    country = CountryField()
    freelance = models.BooleanField(default=False)
    logo = models.ImageField(
        upload_to=os.path.join("images", "companies"),
        storage=DeduplicatedStorage,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered",
            kwargs={
                "_filter": "company",
                "search": self.slug,
            },
        )

    def extended_name_pp(self):
        return "({})".format(self.extended_name) if self.extended_name else ""

    def logo_thumbnail(self):
        return get_image_preview(self.logo.url)

    logo_thumbnail.short_description = "Preview"


class Decoder(models.Model):
    name = models.CharField(max_length=128, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        limit_choices_to={"category": "accessory"},
    )
    version = models.CharField(max_length=64, blank=True)
    sound = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=os.path.join("images", "decoders"),
        storage=DeduplicatedStorage,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["manufacturer__name", "name"]

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)

    image_thumbnail.short_description = "Preview"


class DecoderDocument(Document):
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["decoder", "file"],
                name="unique_decoder_file"
            )
        ]


def calculate_ratio(ratio):
    try:
        num, den = ratio.split(":")
        return int(num) / float(den) * 10000
    except (ValueError, ZeroDivisionError):
        raise ValidationError("Invalid ratio format")


class Scale(models.Model):
    scale = models.CharField(max_length=32, unique=True)
    slug = models.CharField(max_length=32, unique=True, editable=False)
    ratio = models.CharField(max_length=16, validators=[calculate_ratio])
    ratio_int = models.SmallIntegerField(editable=False, default=0)
    tracks = models.FloatField(
        help_text="Distance between model tracks in mm",
    )
    gauge = models.CharField(
        max_length=16,
        blank=True,
        help_text="Distance between real tracks. Please specify the unit (mm, in, ...)",  # noqa: E501
    )

    class Meta:
        ordering = ["-ratio_int", "-tracks", "scale"]

    def get_absolute_url(self):
        return reverse(
            "filtered",
            kwargs={
                "_filter": "scale",
                "search": self.slug,
            },
        )

    def __str__(self):
        return str(self.scale)


@receiver(models.signals.pre_save, sender=Scale)
def scale_save(sender, instance, **kwargs):
    instance.ratio_int = calculate_ratio(instance.ratio)


class RollingStockType(models.Model):
    type = models.CharField(max_length=64)
    order = models.PositiveSmallIntegerField()
    category = models.CharField(
        max_length=64, choices=settings.ROLLING_STOCK_TYPES
    )
    slug = models.CharField(max_length=128, unique=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "type"],
                name="unique_category_type"
            )
        ]
        ordering = ["order"]

    def get_absolute_url(self):
        return reverse(
            "filtered",
            kwargs={
                "_filter": "type",
                "search": self.slug,
            },
        )

    def __str__(self):
        return "{0} {1}".format(self.type, self.category)


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered",
            kwargs={
                "_filter": "tag",
                "search": self.slug,
            },
        )


class GenericDocument(Document):
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = "Generic Documents"


@receiver(models.signals.pre_save, sender=Manufacturer)
@receiver(models.signals.pre_save, sender=Company)
@receiver(models.signals.pre_save, sender=Scale)
@receiver(models.signals.pre_save, sender=RollingStockType)
@receiver(models.signals.pre_save, sender=Tag)
def slug_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.__str__())
