from rest_framework.generics import ListAPIView, RetrieveAPIView

from roster.models import Cab
from roster.serializers import CabSerializer


class RosterList(ListAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer


class RosterGet(RetrieveAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'uuid'


class RosterAddress(RetrieveAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'address'


class RosterIdentifier(RetrieveAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'identifier'
