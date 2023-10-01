import os
import re
from uuid import uuid4
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver

from ckeditor_uploader.fields import RichTextUploadingField

from ram.utils import DeduplicatedStorage, get_image_preview
from ram.models import Document
from metadata.models import (
    Property,
    Scale,
    Manufacturer,
    Decoder,
    Company,
    Tag,
    RollingStockType,
)


class RollingClass(models.Model):
    identifier = models.CharField(max_length=128, unique=False)
    type = models.ForeignKey(RollingStockType, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.CharField(max_length=256, blank=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"category": "real"},
    )

    class Meta:
        ordering = ["company", "identifier"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return "{0} {1}".format(self.company, self.identifier)


class RollingClassProperty(models.Model):
    rolling_class = models.ForeignKey(
        RollingClass,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="property",
        verbose_name="Class",
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.property.name

    class Meta:
        verbose_name_plural = "Properties"


class RollingStock(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    rolling_class = models.ForeignKey(
        RollingClass,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="rolling_class",
        verbose_name="Class",
    )
    road_number = models.CharField(max_length=128, unique=False)
    road_number_int = models.PositiveSmallIntegerField(default=0, unique=False)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"category": "model"},
    )
    scale = models.ForeignKey(Scale, on_delete=models.CASCADE)
    item_number = models.CharField(max_length=32, blank=True)
    decoder_interface = models.PositiveSmallIntegerField(
        choices=settings.DECODER_INTERFACES, null=True, blank=True
    )
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, null=True, blank=True
    )
    address = models.SmallIntegerField(default=None, null=True, blank=True)
    era = models.CharField(max_length=32, blank=True)
    production_year = models.SmallIntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    notes = RichTextUploadingField(blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="rolling_stock", blank=True
    )
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rolling_class", "road_number_int"]
        verbose_name_plural = "Rolling stock"

    def __str__(self):
        return "{0} {1}".format(self.rolling_class, self.road_number)

    def get_absolute_url(self):
        return reverse("rolling_stock", kwargs={"uuid": self.uuid})

    def country(self):
        return str(self.rolling_class.company.country)

    def company(self):
        return str(self.rolling_class.company)


@receiver(models.signals.pre_save, sender=RollingStock)
def pre_save_running_number(sender, instance, *args, **kwargs):
    try:
        instance.road_number_int = int(
            re.findall(r"\d+", instance.road_number)[0]
        )
    except IndexError:
        pass


class RollingStockDocument(Document):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="document"
    )

    class Meta(object):
        unique_together = ("rolling_stock", "file")


class RollingStockImage(models.Model):
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="image"
    )
    image = models.ImageField(
        upload_to="images/", storage=DeduplicatedStorage, null=True, blank=True
    )

    def image_thumbnail(self):
        return get_image_preview(self.image.url)

    image_thumbnail.short_description = "Preview"

    def __str__(self):
        return "{0}".format(os.path.basename(self.image.name))

    class Meta:
        ordering = ["order"]


class RollingStockProperty(models.Model):
    rolling_stock = models.ForeignKey(
        RollingStock,
        on_delete=models.CASCADE,
        related_name="property",
        null=False,
        blank=False,
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.property.name

    class Meta:
        verbose_name_plural = "Properties"


class RollingStockJournal(models.Model):
    rolling_stock = models.ForeignKey(
        RollingStock,
        on_delete=models.CASCADE,
        related_name="journal",
        null=False,
        blank=False,
    )
    date = models.DateField()
    log = RichTextUploadingField()
    private = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.rolling_stock, self.date)

    class Meta:
        ordering = ["date", "rolling_stock"]


# @receiver(models.signals.post_delete, sender=Cab)
# def post_save_image(sender, instance, *args, **kwargs):
#     try:
#         instance.image.delete(save=False)
#     except Exception:
#         pass
