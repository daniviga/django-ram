import django
from django.db import models

from ram import __version__ as app_version
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(
        max_length=256, default="Railroad Assets Manager"
    )
    site_author = models.CharField(max_length=256, blank=True)
    about = models.TextField(blank=True)
    items_per_page = models.CharField(
        max_length=2,
        choices=[(str(x * 3), str(x * 3)) for x in range(2, 11)],
        default="6"
    )
    items_ordering = models.CharField(
        max_length=10,
        choices=[("type", "By rolling stock type"),
                 ("company", "By company name"),
                 ("identifier", "By rolling stock class")],
        default="type"
    )
    footer = models.TextField(blank=True)
    footer_extended = models.TextField(blank=True)
    show_version = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def version(self):
        return app_version

    def django_version(self):
        return django.get_version()
