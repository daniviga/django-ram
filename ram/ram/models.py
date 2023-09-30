import os

from django.db import models
from django.utils.safestring import mark_safe

from ram.utils import DeduplicatedStorage


class Document(models.Model):
    description = models.CharField(max_length=128, blank=True)
    file = models.FileField(
        upload_to="files/",
        storage=DeduplicatedStorage(),
        null=True,
        blank=True,
    )

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
