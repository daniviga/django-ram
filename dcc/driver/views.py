from django.views import View
from django.http import HttpResponse
from driver.serializers import (
    FunctionSerializer, CabSerializer, InfraSerializer)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from dcc.parsers import PlainTextParser
from driver.connector import Connector

conn = Connector()


class SendCommand(APIView):
    parser_classes = [PlainTextParser]

    def put(self, request, address):
        data = request.data
        conn.passthrough(address, data)
        return Response(data,
                        status=status.HTTP_202_ACCEPTED)


class Function(APIView):
    def put(self, request, address):
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            conn.ops(address, serializer.data, function=True)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
