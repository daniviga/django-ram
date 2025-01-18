import os

from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from ram.models import BaseModel
from ram.utils import DeduplicatedStorage
from metadata.models import Company, Tag
from roster.models import RollingStock


class Consist(BaseModel):
    identifier = models.CharField(max_length=128, unique=False)
    tags = models.ManyToManyField(Tag, related_name="consist", blank=True)
    consist_address = models.SmallIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="DCC consist address if enabled",
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    era = models.CharField(
        max_length=32,
        blank=True,
        help_text="Era or epoch of the consist",
    )
    image = models.ImageField(
        upload_to=os.path.join("images", "consists"),
        storage=DeduplicatedStorage,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "{0} {1}".format(self.company, self.identifier)

    def get_absolute_url(self):
        return reverse("consist", kwargs={"uuid": self.uuid})

    @property
    def country(self):
        return self.company.country

    def clean(self):
        if self.consist_item.filter(rolling_stock__published=False).exists():
            raise ValidationError(
                "You must publish all items in the consist before publishing the consist."  # noqa: E501
            )

    class Meta:
        ordering = ["company", "-creation_time"]


class ConsistItem(models.Model):
    consist = models.ForeignKey(
        Consist, on_delete=models.CASCADE, related_name="consist_item"
    )
    rolling_stock = models.ForeignKey(RollingStock, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        default=1000,  # make sure it is always added at the end
        blank=False,
        null=False
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["consist", "rolling_stock"],
                name="one_stock_per_consist"
            )
        ]

    def __str__(self):
        return "{0}".format(self.rolling_stock)

    def published(self):
        return self.rolling_stock.published
    published.boolean = True

    def preview(self):
        return self.rolling_stock.image.first().image_thumbnail(100)

    @property
    def type(self):
        return self.rolling_stock.rolling_class.type

    @property
    def address(self):
        return self.rolling_stock.address

    @property
    def company(self):
        return self.rolling_stock.company

    @property
    def era(self):
        return self.rolling_stock.era


# Unpublish any consist that contains an unpublished rolling stock
# this signal is called after a rolling stock is saved
# it is hosted here to avoid circular imports
@receiver(models.signals.post_save, sender=RollingStock)
def post_save_unpublish_consist(sender, instance, *args, **kwargs):
    consists = Consist.objects.filter(consist_item__rolling_stock=instance)
    for consist in consists:
        consist.published = False
        consist.save()
