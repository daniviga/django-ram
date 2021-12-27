from rest_framework import serializers
from roster.models import Cab
from metadata.serializers import (
    ManufacturerSerializer, CompanySerializer, DecoderSerializer)


class CabSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer()
    decoder = DecoderSerializer()
    company = CompanySerializer()
    # manufacturer = serializers.StringRelatedField()
    # decoder = serializers.StringRelatedField()
    # company = serializers.StringRelatedField()

    class Meta:
        model = Cab
        fields = "__all__"
        read_only_fields = ("identifier", "creation_time", "updated_time")
