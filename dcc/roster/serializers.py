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
        fields = "__all__"
        read_only_fields = ("creation_time", "updated_time")
