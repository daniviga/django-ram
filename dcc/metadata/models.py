from django.db import models
from django.dispatch.dispatcher import receiver
from django_countries.fields import CountryField

from dcc.utils import get_image_preview, slugify


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)
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
    name = models.CharField(max_length=128, unique=True)
    country = CountryField()
    logo = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def logo_thumbnail(self):
        return get_image_preview(self.logo.url)
    logo_thumbnail.short_description = "Preview"


class Decoder(models.Model):
    class Interface(models.IntegerChoices):
        NEM651 = 1, "NEM651"
        NEM652 = 2, "NEM652"
        NEM658 = 3, "PluX"
        NEM660 = 4, "21MTC"
        NEM662 = 5, "Next18/Next18S"

    name = models.CharField(max_length=128, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE)
    version = models.CharField(max_length=64, blank=True)
    interface = models.PositiveSmallIntegerField(
        choices=Interface.choices,
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)
    image_thumbnail.short_description = "Preview"


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


@receiver(models.signals.pre_save, sender=Tag)
def tag_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)
