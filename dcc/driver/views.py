from django.views import View
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from dcc.parsers import PlainTextParser
from driver.connector import Connector
from driver.serializers import (
    FunctionSerializer, CabSerializer, InfraSerializer)
from roster.models import Cab as CabModel

conn = Connector()


def addresschecker(f):
    def addresslookup(request, address, *args):
        try:
            CabModel.objects.get(address=address)
        except CabModel.DoesNotExist:
            raise Http404
        return f(request, address, *args)
    return addresslookup


@method_decorator(addresschecker, name="put")
class SendCommand(APIView):
    parser_classes = [PlainTextParser]

    def put(self, request, address):
        data = request.data
        conn.passthrough(address, data)
        return Response(data,
                        status=status.HTTP_202_ACCEPTED)


@method_decorator(addresschecker, name="put")
class Function(APIView):
    def put(self, request, address):
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            conn.ops(address, serializer.data, function=True)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


@method_decorator(addresschecker, name="put")
class Cab(APIView):
    def put(self, request, address):
        serializer = CabSerializer(data=request.data)
        if serializer.is_valid():
            conn.ops(address, serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class Infra(APIView):
    def put(self, request):
        serializer = InfraSerializer(data=request.data)
        if serializer.is_valid():
            conn.infra(serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class Emergency(View):
    def put(self, request):
        conn.emergency()
        return HttpResponse()

    def get(self, request):
        conn.emergency()
        return HttpResponse()
