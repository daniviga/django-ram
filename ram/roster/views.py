from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.schemas.openapi import AutoSchema

from ram.views import CustomLimitOffsetPagination
from roster.models import RollingStock
from roster.serializers import RollingStockSerializer


class RosterList(ListAPIView):
    serializer_class = RollingStockSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return RollingStock.objects.get_published(self.request.user)


class RosterGet(RetrieveAPIView):
    serializer_class = RollingStockSerializer
    lookup_field = "uuid"
    schema = AutoSchema(operation_id_base="retrieveRollingStockByUUID")

    def get_queryset(self):
        return RollingStock.objects.get_published(self.request.user)


class RosterAddress(ListAPIView):
    serializer_class = RollingStockSerializer
    pagination_class = CustomLimitOffsetPagination
    schema = AutoSchema(operation_id_base="retrieveRollingStockByAddress")

    def get_queryset(self):
        address = self.kwargs["address"]
        return RollingStock.objects.get_published(self.request.user).filter(
            address=address
        )


class RosterClass(ListAPIView):
    serializer_class = RollingStockSerializer
    pagination_class = CustomLimitOffsetPagination

    schema = AutoSchema(operation_id_base="retrieveRollingStockByClass")

    def get_queryset(self):
        _class = self.kwargs["class"]
        return RollingStock.objects.get_published(self.request.user).filter(
            rolling_class__identifier=_class
        )
