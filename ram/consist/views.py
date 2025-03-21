from rest_framework.generics import ListAPIView, RetrieveAPIView

from ram.views import CustomLimitOffsetPagination
from consist.models import Consist
from consist.serializers import ConsistSerializer


class ConsistList(ListAPIView):
    serializer_class = ConsistSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Consist.objects.get_published(self.request.user)


class ConsistGet(RetrieveAPIView):
    serializer_class = ConsistSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return Consist.objects.get_published(self.request.user)
