from rest_framework import serializers
from metadata.models import (
    RollingStockType, Scale, Manufacturer,
    Company, Decoder, Tag)


class RollingStockTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RollingStockType
        fields = "__all__"


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class ScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scale
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class DecoderSerializer(serializers.ModelSerializer):
    manufacturer = serializers.StringRelatedField()

    class Meta:
        model = Decoder
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
