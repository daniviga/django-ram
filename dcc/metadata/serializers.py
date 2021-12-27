from rest_framework import serializers
from metadata.models import Manufacturer, Company, Decoder


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
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
