import os

from django.db import models
from django.urls import reverse
from django.utils.text import Truncator
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from ram.models import BaseModel
from ram.utils import DeduplicatedStorage
from ram.managers import ConsistManager
from metadata.models import Company, Scale, Tag
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
    scale = models.ForeignKey(Scale, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=os.path.join("images", "consists"),
        storage=DeduplicatedStorage,
        null=True,
        blank=True,
    )

    objects = ConsistManager()

    def __str__(self):
        return "{0} {1}".format(self.company, self.identifier)

    def get_absolute_url(self):
        return reverse("consist", kwargs={"uuid": self.uuid})

    @property
    def length(self):
        return self.consist_item.filter(load=False).count()

    def get_type_count(self):
        return self.consist_item.filter(load=False).annotate(
            type=models.F("rolling_stock__rolling_class__type__type")
        ).values(
            "type"
        ).annotate(
            count=models.Count("rolling_stock"),
            category=models.F("rolling_stock__rolling_class__type__category"),
            order=models.Max("order"),
        ).order_by("order")

    def get_cover(self):
        if self.image:
            return self.image
        else:
            consist_item = self.consist_item.first()
            if consist_item and consist_item.rolling_stock.image.exists():
                return consist_item.rolling_stock.image.first().image
        return None

    @property
    def country(self):
        return self.company.country

    class Meta:
        ordering = ["company", "-creation_time"]


class ConsistItem(models.Model):
    consist = models.ForeignKey(
        Consist, on_delete=models.CASCADE, related_name="consist_item"
    )
    rolling_stock = models.ForeignKey(RollingStock, on_delete=models.CASCADE)
    load = models.BooleanField(default=False)
    order = models.PositiveIntegerField(blank=False, null=False)

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

    def clean(self):
        rolling_stock = getattr(self, "rolling_stock", False)
        if not rolling_stock:
            return  # exit if no inline are present

        # FIXME this does not work when creating a new consist,
        # because the consist is not saved yet and it must be moved
        # to the admin form validation via InlineFormSet.clean()
        consist = self.consist
        # Scale must match, but allow loads of any scale
        if rolling_stock.scale != consist.scale and not self.load:
            raise ValidationError(
                "The rolling stock and consist must be of the same scale."
            )
        if self.load and rolling_stock.scale.ratio != consist.scale.ratio:
            raise ValidationError(
                "The load and consist must be of the same scale ratio."
            )
        if self.consist.published and not rolling_stock.published:
            raise ValidationError(
                "You must unpublish the the consist before using this item."
            )

    def published(self):
        return self.rolling_stock.published
    published.boolean = True

    def preview(self):
        return self.rolling_stock.image.first().image_thumbnail(100)

    @property
    def manufacturer(self):
        return Truncator(self.rolling_stock.manufacturer).chars(10)

    @property
    def item_number(self):
        return self.rolling_stock.item_number

    @property
    def scale(self):
        return self.rolling_stock.scale

    @property
    def type(self):
        return self.rolling_stock.rolling_class.type.type

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
    if not instance.published:
        consists = Consist.objects.filter(consist_item__rolling_stock=instance)
        for consist in consists:
            consist.published = False
            consist.save()
