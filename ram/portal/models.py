import django
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.dispatch.dispatcher import receiver
from django.utils.safestring import mark_safe
from solo.models import SingletonModel

from tinymce import models as tinymce

from ram import __version__ as app_version
from ram.managers import PublicManager
from ram.utils import slugify


class SiteConfiguration(SingletonModel):
    site_author = models.CharField(max_length=256, blank=True)
    about = tinymce.HTMLField(blank=True)
    items_per_page = models.CharField(
        max_length=2,
        choices=[(str(x * 3), str(x * 3)) for x in range(2, 11)],
        default="6",
    )
    items_ordering = models.CharField(
        max_length=11,
        choices=[
            ("type", "By rolling stock type and company"),
            ("class", "By rolling stock type and class"),
            ("company", "By company and type"),
            ("country", "By country and type"),
            ("cou+com", "By country and company"),
        ],
        default="type",
    )
    featured_items_ordering = items_ordering.clone()
    currency = models.CharField(max_length=3, default="EUR")
    footer = tinymce.HTMLField(blank=True)
    footer_extended = tinymce.HTMLField(blank=True)
    disclaimer = tinymce.HTMLField(blank=True)
    show_version = models.BooleanField(default=True)
    use_cdn = models.BooleanField(default=True)
    extra_html = models.TextField(
        blank=True,
        help_text="Extra HTML to be dinamically loaded into the site.",
    )
    extra_js = models.TextField(
        blank=True,
        help_text="Extra JS to be dinamically loaded into the site.",
    )

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def site_name(self):
        return settings.SITE_NAME

    @property
    def version(self):
        return app_version

    @property
    def django_version(self):
        return django.get_version()


class Flatpage(models.Model):
    name = models.CharField(max_length=256, unique=True)
    path = models.CharField(max_length=256, unique=True)
    published = models.BooleanField(default=False)
    content = tinymce.HTMLField()
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "page"
        verbose_name_plural = "pages"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("flatpage", kwargs={"flatpage": self.path})

    def get_link(self):
        return mark_safe(
            '<a href="{0}" target="_blank">Link</a>'.format(
                self.get_absolute_url()
            )
        )

    objects = PublicManager()


@receiver(models.signals.pre_save, sender=Flatpage)
def tag_pre_save(sender, instance, **kwargs):
    instance.path = slugify(instance.name)
