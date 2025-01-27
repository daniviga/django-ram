from rest_framework import serializers
from roster.models import RollingClass, RollingStock
from metadata.serializers import (
    RollingStockTypeSerializer,
    ManufacturerSerializer,
    ScaleSerializer,
    CompanySerializer,
    DecoderSerializer,
    TagSerializer,
)


class RollingClassSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(many=True)
    company = CompanySerializer()
    type = RollingStockTypeSerializer()

    class Meta:
        model = RollingClass
        fields = "__all__"


class RollingStockSerializer(serializers.ModelSerializer):
    rolling_class = RollingClassSerializer()
    manufacturer = ManufacturerSerializer()
    decoder = DecoderSerializer()
    scale = ScaleSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = RollingStock
        exclude = (
            "notes",
            "shop",
            "purchase_date",
            "price",
        )
        read_only_fields = ("creation_time", "updated_time")
