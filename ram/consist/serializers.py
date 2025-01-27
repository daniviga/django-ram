from rest_framework import serializers
from consist.models import Consist, ConsistItem

from metadata.serializers import CompanySerializer, TagSerializer

# from roster.serializers import RollingStockSerializer


class ConsistItemSerializer(serializers.ModelSerializer):
    # rolling_stock = RollingStockSerializer()

    class Meta:
        model = ConsistItem
        fields = ("order", "rolling_stock")


class ConsistSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    consist_item = ConsistItemSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Consist
        exclude = ("notes",)
        read_only_fields = ("creation_time", "updated_time")
