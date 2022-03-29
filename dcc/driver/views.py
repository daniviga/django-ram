from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from dcc.parsers import PlainTextParser
from driver.connector import Connector
from driver.serializers import (
    FunctionSerializer, CabSerializer, InfraSerializer)
from roster.models import RollingStock


def addresschecker(f):
    """
    Check if DCC address does exist in the database
    """
    def addresslookup(request, address, *args):
        try:
            RollingStock.objects.get(address=address)
        except RollingStock.DoesNotExist:
            raise Http404
        return f(request, address, *args)
    return addresslookup


class Test(APIView):
    """
    Send a test <s> command
    """
    parser_classes = [PlainTextParser]

    def get(self, request):
        response = Connector().passthrough("<s>")
        return Response({"response": response.decode()},
                        status=status.HTTP_202_ACCEPTED)


class SendCommand(APIView):
    """
    Command passthrough
    """
    parser_classes = [PlainTextParser]

    def put(self, request):
        data = request.data
        if not data:
            raise serializers.ValidationError({
                "error": "a string is expected"})
        cmd = data.decode().strip()
        if not (cmd.startswith("<") and cmd.endswith(">")):
            raise serializers.ValidationError({
                "error": "please provide a valid command"})
        response = Connector().passthrough(cmd)
        return Response({"response": response.decode()},
                        status=status.HTTP_202_ACCEPTED)


@method_decorator(addresschecker, name="put")
class Function(APIView):
    """
    Send "Function" commands to a valid DCC address
    """
    def put(self, request, address):
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            Connector().ops(address, serializer.data, function=True)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


@method_decorator(addresschecker, name="put")
class Cab(APIView):
    """
    Send "Cab" commands to a valid DCC address
    """
    def put(self, request, address):
        serializer = CabSerializer(data=request.data)
        if serializer.is_valid():
            Connector().ops(address, serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class Infra(APIView):
    """
    Send "Infra" commands to a valid DCC address
    """
    def put(self, request):
        serializer = InfraSerializer(data=request.data)
        if serializer.is_valid():
            Connector().infra(serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class Emergency(APIView):
    """
    Send an "Emergency" stop, no matter the HTTP method used
    """
    def put(self, request):
        Connector().emergency()
        return Response({"response": "emergency stop"},
                        status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        Connector().emergency()
        return Response({"response": "emergency stop"},
                        status=status.HTTP_202_ACCEPTED)
