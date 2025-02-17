import os
from uuid import uuid4

from django.db import models
from django.utils.safestring import mark_safe
from tinymce import models as tinymce

from ram.utils import DeduplicatedStorage, get_image_preview
from ram.managers import PublicManager


class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = tinymce.HTMLField(blank=True)
    notes = tinymce.HTMLField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    class Meta:
        abstract = True

    objects = PublicManager()


class Document(models.Model):
    description = models.CharField(max_length=128, blank=True)
    file = models.FileField(
        upload_to="files/",
    )
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        verbose_name_plural = "Documents"

    def __str__(self):
        return "{0}".format(os.path.basename(self.file.name))

    @property
    def filename(self):
        return self.__str__()

    @property
    def size(self):
        kb = self.file.size / 1024.0
        if kb < 1024:
            size = "{0} KB".format(round(kb))
        else:
            size = "{0} MB".format(round(kb / 1024.0))
        return size

    def download(self):
        return mark_safe(
            '<a href="{0}" target="_blank">Link</a>'.format(self.file.url)
        )


class PrivateDocument(Document):
    private = models.BooleanField(
        default=False,
        help_text="Document will be visible only to logged users",
    )
    objects = PublicManager()

    class Meta:
        abstract = True


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
        verbose_name_plural = "Images"

    objects = PublicManager()


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

    objects = PublicManager()
