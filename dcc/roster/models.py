from uuid import uuid4
from django.db import models
# from django.core.files.storage import FileSystemStorage
# from django.dispatch import receiver

from dcc.utils import get_image_preview


# class OverwriteMixin(FileSystemStorage):
#     def get_available_name(self, name, max_length):
#         self.delete(name)
#         return name


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=128, unique=True)
    country = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name



class Decoder(models.Model):
    name = models.CharField(max_length=128, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)


class Cab(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid4,
        editable=False)
    identifier = models.CharField(max_length=128, unique=False)
    address = models.SmallIntegerField(default=3)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE,
        null=True, blank=True)
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE,
        null=True, blank=True)
    epoch = models.CharField(max_length=32, blank=True)
    production_year = models.SmallIntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)

    image = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True)
    notes = models.TextField(blank=True)

    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['address', 'identifier']

    def __str__(self):
        return "{0} {1}".format(self.manufacturer, self.identifier)

    def image_thumbnail(self):
        return get_image_preview(self.image.url)
    image_thumbnail.short_description = "Preview"


# @receiver(models.signals.post_delete, sender=Cab)
# def post_save_image(sender, instance, *args, **kwargs):
#     try:
#         instance.image.delete(save=False)
#     except Exception:
#         pass
