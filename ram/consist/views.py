from rest_framework.generics import ListAPIView, RetrieveAPIView

from consist.models import Consist
from consist.serializers import ConsistSerializer


class ConsistList(ListAPIView):
    queryset = Consist.objects.all()
    serializer_class = ConsistSerializer


class ConsistGet(RetrieveAPIView):
    queryset = Consist.objects.all()
    serializer_class = ConsistSerializer
    lookup_field = "uuid"
