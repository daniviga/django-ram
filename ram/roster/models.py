import os
import re
import shutil
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver

from tinymce import models as tinymce

from ram.models import BaseModel, Document, Image, PropertyInstance
from ram.utils import DeduplicatedStorage, slugify
from ram.managers import PublicManager
from metadata.models import (
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
    description = tinymce.HTMLField(blank=True)
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

    @property
    def country(self):
        return self.company.country


class RollingClassProperty(PropertyInstance):
    rolling_class = models.ForeignKey(
        RollingClass,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="property",
        verbose_name="Class",
    )


class RollingStock(BaseModel):
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
    item_number = models.CharField(
        max_length=32,
        blank=True,
        help_text="Catalog item number or code",
    )
    item_number_slug = models.CharField(
        max_length=32,
        blank=True,
        editable=False
    )
    set = models.BooleanField(
        default=False,
        help_text="Part of a set",
    )
    decoder_interface = models.PositiveSmallIntegerField(
        choices=settings.DECODER_INTERFACES, null=True, blank=True
    )
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, null=True, blank=True
    )
    address = models.SmallIntegerField(default=None, null=True, blank=True)
    era = models.CharField(
        max_length=32,
        blank=True,
        help_text="Era or epoch of the model",
    )
    production_year = models.SmallIntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    description = tinymce.HTMLField(blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="rolling_stock", blank=True
    )

    class Meta:
        ordering = ["rolling_class", "road_number_int"]
        verbose_name_plural = "Rolling stock"

    def __str__(self):
        return "{0} {1}".format(self.rolling_class, self.road_number)

    def get_absolute_url(self):
        return reverse("rolling_stock", kwargs={"uuid": self.uuid})

    def preview(self):
        return self.image.first().image_thumbnail(350)

    @property
    def country(self):
        return self.rolling_class.company.country

    @property
    def company(self):
        return self.rolling_class.company

    def delete(self, *args, **kwargs):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "images", "rollingstock", str(self.uuid)
            ),
            ignore_errors=True
        )
        super(RollingStock, self).delete(*args, **kwargs)


@receiver(models.signals.pre_save, sender=RollingStock)
def pre_save_internal_fields(sender, instance, *args, **kwargs):
    # Extract road number integer from road number
    try:
        instance.road_number_int = int(
            re.findall(r"\d+", instance.road_number)[0]
        )
    except IndexError:
        pass
    # Generate a machine-friendly item number from original item number
    instance.item_number_slug = slugify(instance.item_number)


class RollingStockDocument(Document):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rolling_stock", "file"],
                name="unique_stock_file"
            )
        ]


def rolling_stock_image_upload(instance, filename):
    return os.path.join(
        "images",
        "rollingstock",
        str(instance.rolling_stock.uuid),
        filename
    )


class RollingStockImage(Image):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="image"
    )
    image = models.ImageField(
        upload_to=rolling_stock_image_upload,
        storage=DeduplicatedStorage,
    )


class RollingStockProperty(PropertyInstance):
    rolling_stock = models.ForeignKey(
        RollingStock,
        on_delete=models.CASCADE,
        related_name="property",
        null=False,
        blank=False,
    )


class RollingStockJournal(models.Model):
    rolling_stock = models.ForeignKey(
        RollingStock,
        on_delete=models.CASCADE,
        related_name="journal",
        null=False,
        blank=False,
    )
    date = models.DateField()
    log = tinymce.HTMLField()
    private = models.BooleanField(
        default=False,
        help_text="Journal log will be visible only to logged users",
    )
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.rolling_stock, self.date)

    class Meta:
        ordering = ["date", "rolling_stock"]

    objects = PublicManager()


# @receiver(models.signals.post_delete, sender=Cab)
# def post_save_image(sender, instance, *args, **kwargs):
#     try:
#         instance.image.delete(save=False)
#     except Exception:
#         pass
