from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.schemas.openapi import AutoSchema

from roster.models import RollingStock
from roster.serializers import RollingStockSerializer


class RosterList(ListAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer


class RosterGet(RetrieveAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer
    lookup_field = "uuid"

    schema = AutoSchema(
        operation_id_base="retrieveRollingStockByUUID"
    )


class RosterAddress(ListAPIView):
    serializer_class = RollingStockSerializer

    schema = AutoSchema(
        operation_id_base="retrieveRollingStockByAddress"
    )

    def get_queryset(self):
        address = self.kwargs["address"]
        return RollingStock.objects.filter(address=address)


class RosterClass(ListAPIView):
    serializer_class = RollingStockSerializer

    schema = AutoSchema(
        operation_id_base="retrieveRollingStockByClass"
    )

    def get_queryset(self):
        _class = self.kwargs["class"]
        return RollingStock.objects.filter(rolling_class__identifier=_class)
