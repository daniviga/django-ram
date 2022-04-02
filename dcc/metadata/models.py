from django.db import models
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django_countries.fields import CountryField

from dcc.utils import get_image_preview, slugify


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    def __str__(self):
        return self.name

    def logo_thumbnail(self):
        return get_image_preview(self.logo.url)
    logo_thumbnail.short_description = "Preview"


class Company(models.Model):
    name = models.CharField(max_length=64, unique=True)
    extended_name = models.CharField(max_length=128, blank=True)
    country = CountryField()
    freelance = models.BooleanField(default=False)
    logo = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

    def logo_thumbnail(self):
        return get_image_preview(self.logo.url)
    logo_thumbnail.short_description = "Preview"


class Decoder(models.Model):
    name = models.CharField(max_length=128, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE)
    version = models.CharField(max_length=64, blank=True)
    interface = models.PositiveSmallIntegerField(
        choices=settings.DECODER_INTERFACES,
        null=True,
        blank=True
    )
    sound = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)
    image_thumbnail.short_description = "Preview"


class Scale(models.Model):
    scale = models.CharField(max_length=32, unique=True)
    ratio = models.CharField(max_length=16, blank=True)
    gauge = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ['scale']

    def __str__(self):
        return str(self.scale)


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


@receiver(models.signals.pre_save, sender=Tag)
def tag_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)


class RollingStockType(models.Model):
    type = models.CharField(max_length=64)
    category = models.CharField(
        max_length=64, choices=settings.ROLLING_STOCK_TYPES)

    class Meta(object):
        unique_together = ('category', 'type')

    def __str__(self):
        return "{0} {1}".format(self.type, self.category)
