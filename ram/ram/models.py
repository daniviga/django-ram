import os

from django.db import models
from django.utils.safestring import mark_safe

from ram.utils import DeduplicatedStorage, get_image_preview


class Document(models.Model):
    description = models.CharField(max_length=128, blank=True)
    file = models.FileField(
        upload_to="files/",
        storage=DeduplicatedStorage(),
    )
    private = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return "{0}".format(os.path.basename(self.file.name))

    def filename(self):
        return self.__str__()

    def download(self):
        return mark_safe(
            '<a href="{0}" target="_blank">Link</a>'.format(self.file.url)
        )


class Image(models.Model):
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    image = models.ImageField(
        upload_to="images/",
        storage=DeduplicatedStorage,
    )

    def image_thumbnail(self, max_size=150):
        return get_image_preview(self.image.url, max_size)

    image_thumbnail.short_description = "Preview"

    def __str__(self):
        return "{0}".format(os.path.basename(self.image.name))

    class Meta:
        abstract = True
        ordering = ["order"]


class PropertyInstance(models.Model):
    property = models.ForeignKey(
        "metadata.Property",  # To avoid circular dependencies
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.property.name

    class Meta:
        abstract = True
        verbose_name_plural = "Properties"
