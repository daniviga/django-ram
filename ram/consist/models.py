from uuid import uuid4
from django.db import models

from metadata.models import Company, Tag
from roster.models import RollingStock


class Consist(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    identifier = models.CharField(max_length=128, unique=False)
    tags = models.ManyToManyField(Tag, related_name="consist", blank=True)
    consist_address = models.SmallIntegerField(
        default=None, null=True, blank=True
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    era = models.CharField(max_length=32, blank=True)
    notes = models.TextField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.identifier)


class ConsistItem(models.Model):
    consist = models.ForeignKey(
        Consist, on_delete=models.CASCADE, related_name="consist_item"
    )
    rolling_stock = models.ForeignKey(RollingStock, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return "{0}".format(self.rolling_stock)

    def type(self):
        return self.rolling_stock.rolling_class.type

    def address(self):
        return self.rolling_stock.address

    def company(self):
        return self.rolling_stock.company()

    def era(self):
        return self.rolling_stock.era
