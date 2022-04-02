from rest_framework import serializers
from roster.models import RollingStock
from metadata.serializers import (
    ManufacturerSerializer, CompanySerializer, DecoderSerializer)


class RollingStockSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer()
    decoder = DecoderSerializer()
    company = CompanySerializer()

    class Meta:
        model = RollingStock
        fields = "__all__"
        read_only_fields = ("creation_time", "updated_time")
