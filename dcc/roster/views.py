from rest_framework.generics import ListAPIView, RetrieveAPIView

from roster.models import RollingStock
from roster.serializers import RollingStockSerializer


class RosterList(ListAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer


class RosterGet(RetrieveAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer
    lookup_field = 'uuid'


class RosterAddress(ListAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer
    lookup_field = 'address'


class RosterIdentifier(RetrieveAPIView):
    queryset = RollingStock.objects.all()
    serializer_class = RollingStockSerializer
    lookup_field = 'identifier'
