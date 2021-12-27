from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

from roster.models import Cab
from roster.serializers import CabSerializer


class RosterList(ListCreateAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer


class RosterGet(RetrieveUpdateAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'uuid'


class RosterAddress(RetrieveUpdateAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'address'


class RosterIdentifier(RetrieveUpdateAPIView):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    lookup_field = 'identifier'
