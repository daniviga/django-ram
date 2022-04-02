import os
from uuid import uuid4
from django.db import models
# from django.core.files.storage import FileSystemStorage
# from django.dispatch import receiver

from dcc.utils import get_image_preview
from metadata.models import (
    Manufacturer, Decoder, Company, Tag, RollingStockType)

# class OverwriteMixin(FileSystemStorage):
#     def get_available_name(self, name, max_length):
#         self.delete(name)
#         return name


class RollingStock(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid4,
        editable=False)
    identifier = models.CharField(max_length=128, unique=False)
    tags = models.ManyToManyField(
        Tag,
        related_name='rolling_stock',
        blank=True)
    address = models.SmallIntegerField(default=None, null=True, blank=True)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE,
        null=True, blank=True)
    sku = models.CharField(max_length=32, blank=True)
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE,
        null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        null=True, blank=True)
    epoch = models.CharField(max_length=32, blank=True)
    production_year = models.SmallIntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['address', 'identifier']
        verbose_name_plural = "Rolling stock"

    def __str__(self):
        return "{0} {1}".format(self.manufacturer, self.identifier)


class Engine(RollingStock):
    type = models.ForeignKey(
        RollingStockType, on_delete=models.CASCADE,
        limit_choices_to={'category': 'engine'},
        null=True, blank=True)


class Car(RollingStock):
    type = models.ForeignKey(
        RollingStockType, on_delete=models.CASCADE,
        limit_choices_to={'category': 'car'},
        null=True, blank=True)


class Equipment(RollingStock):
    type = models.ForeignKey(
        RollingStockType, on_delete=models.CASCADE,
        limit_choices_to={'category': 'equipment'},
        null=True, blank=True)


class Other(RollingStock):
    type = models.ForeignKey(
        RollingStockType, on_delete=models.CASCADE,
        limit_choices_to={'category': 'other'},
        null=True, blank=True)


class RollingStockDocument(models.Model):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE)
    description = models.CharField(max_length=128, blank=True)
    file = models.FileField(
        upload_to='files/',
        null=True,
        blank=True)

    class Meta(object):
        unique_together = ('rolling_stock', 'file')

    def __str__(self):
        return "{0}".format(os.path.basename(self.file.name))
        # return "{0}".format(self.description)


class RollingStockImage(models.Model):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)
    image_thumbnail.short_description = "Preview"

    class Meta(object):
        unique_together = ('rolling_stock', 'image')

    def __str__(self):
        return "{0}".format(os.path.basename(self.image.name))

# @receiver(models.signals.post_delete, sender=Cab)
# def post_save_image(sender, instance, *args, **kwargs):
#     try:
#         instance.image.delete(save=False)
#     except Exception:
#         pass
