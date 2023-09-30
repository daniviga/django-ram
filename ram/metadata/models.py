import os

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.dispatch.dispatcher import receiver
from django_countries.fields import CountryField

from ram.utils import DeduplicatedStorage, get_image_preview, slugify


class Property(models.Model):
    name = models.CharField(max_length=128, unique=True)
    private = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True, editable=False)
    category = models.CharField(
        max_length=64, choices=settings.MANUFACTURER_TYPES
    )
    website = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to="images/", storage=DeduplicatedStorage, null=True, blank=True
    )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered", kwargs={
                "_filter": "manufacturer",
                "search": self.slug,
            }
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
        upload_to="images/", storage=DeduplicatedStorage, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered", kwargs={
                "_filter": "company",
                "search": self.slug,
            }
        )

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
        upload_to="images/", storage=DeduplicatedStorage, null=True, blank=True
    )

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)

    image_thumbnail.short_description = "Preview"


class DecoderDocument(models.Model):
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, related_name="document"
    )
    description = models.CharField(max_length=128, blank=True)
    file = models.FileField(
        upload_to="files/",
        storage=DeduplicatedStorage(),
        null=True,
        blank=True,
    )

    class Meta(object):
        unique_together = ("decoder", "file")

    def __str__(self):
        return "{0}".format(os.path.basename(self.file.name))

    def filename(self):
        return self.__str__()

    def download(self):
        return mark_safe(
            '<a href="{0}" target="_blank">Link</a>'.format(self.file.url)
        )


class Scale(models.Model):
    scale = models.CharField(max_length=32, unique=True)
    slug = models.CharField(max_length=32, unique=True, editable=False)
    ratio = models.CharField(max_length=16, blank=True)
    gauge = models.CharField(max_length=16, blank=True)
    tracks = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["scale"]

    def get_absolute_url(self):
        return reverse(
            "filtered", kwargs={
                "_filter": "scale",
                "search": self.slug,
            }
        )

    def __str__(self):
        return str(self.scale)


class RollingStockType(models.Model):
    type = models.CharField(max_length=64)
    order = models.PositiveSmallIntegerField()
    category = models.CharField(
        max_length=64, choices=settings.ROLLING_STOCK_TYPES
    )
    slug = models.CharField(max_length=128, unique=True, editable=False)

    class Meta(object):
        unique_together = ("category", "type")
        ordering = ["order"]

    def get_absolute_url(self):
        return reverse(
            "filtered", kwargs={
                "_filter": "type",
                "search": self.slug,
            }
        )

    def __str__(self):
        return "{0} {1}".format(self.type, self.category)


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "filtered", kwargs={
                "_filter": "tag",
                "search": self.slug,
            }
        )



@receiver(models.signals.pre_save, sender=Manufacturer)
@receiver(models.signals.pre_save, sender=Company)
@receiver(models.signals.pre_save, sender=Scale)
@receiver(models.signals.pre_save, sender=RollingStockType)
@receiver(models.signals.pre_save, sender=Tag)
def slug_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.__str__())
