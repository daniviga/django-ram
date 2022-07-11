from ipaddress import IPv4Address, IPv4Network
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    BasePermission,
    SAFE_METHODS,
)

from ram.parsers import PlainTextParser
from driver.models import DriverConfiguration
from driver.connector import Connector
from driver.serializers import (
    FunctionSerializer,
    CabSerializer,
    InfraSerializer,
)
from roster.models import RollingStock


def addresschecker(f):
    """
    Check if DCC address does exist in the database
    """

    def addresslookup(request, address, *args):
        if not RollingStock.objects.filter(address=address):
            raise Http404
        return f(request, address, *args)

    return addresslookup


class IsEnabled(BasePermission):
    def has_permission(self, request, view):
        config = DriverConfiguration.get_solo()

        # if driver is disabled, block all connections
        if not config.enabled:
            raise Http404

        return True


class Firewall(BasePermission):
    def has_permission(self, request, view):
        config = DriverConfiguration.get_solo()

        # if network is not configured, accept only read ops
        if not config.network:
            return request.method in SAFE_METHODS

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = IPv4Address(x_forwarded_for.split(",")[0])
        else:
            ip = IPv4Address(request.META.get("REMOTE_ADDR"))

        network = IPv4Network(
            "{0}/{1}".format(config.network, config.subnet_mask)
        )

        # accept IP configured is settings or localhost
        if ip in network or ip in IPv4Network("127.0.0.0/8"):
            return True


class Test(APIView):
    """
    Send a test 's' command
    """

    parser_classes = [PlainTextParser]
    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def get(self, request):
        response = Connector().passthrough("<s>")
        return Response(
            {"response": response.decode()}, status=status.HTTP_202_ACCEPTED
        )


class SendCommand(APIView):
    """
    Command passthrough
    """

    parser_classes = [PlainTextParser]
    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def put(self, request):
        data = request.data
        if not data:
            raise serializers.ValidationError(
                {"error": "a string is expected"}
            )
        cmd = data.decode().strip()
        if not (cmd.startswith("<") and cmd.endswith(">")):
            raise serializers.ValidationError(
                {"error": "please provide a valid command"}
            )
        response = Connector().passthrough(cmd)
        return Response(
            {"response": response.decode()}, status=status.HTTP_202_ACCEPTED
        )


@method_decorator(addresschecker, name="put")
class Function(APIView):
    """
    Send "Function" commands to a valid DCC address
    """

    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def put(self, request, address):
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            Connector().ops(address, serializer.data, function=True)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(addresschecker, name="put")
class Cab(APIView):
    """
    Send "Cab" commands to a valid DCC address
    """

    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def put(self, request, address):
        serializer = CabSerializer(data=request.data)
        if serializer.is_valid():
            Connector().ops(address, serializer.data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Infra(APIView):
    """
    Send "Infra" commands to a valid DCC address
    """

    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def put(self, request):
        serializer = InfraSerializer(data=request.data)
        if serializer.is_valid():
            Connector().infra(serializer.data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Emergency(APIView):
    """
    Send an "Emergency" stop, no matter the HTTP method used
    """

    permission_classes = [IsEnabled & IsAuthenticated | Firewall]

    def put(self, request):
        Connector().emergency()
        return Response(
            {"response": "emergency stop"}, status=status.HTTP_202_ACCEPTED
        )

    def get(self, request):
        Connector().emergency()
        return Response(
            {"response": "emergency stop"}, status=status.HTTP_202_ACCEPTED
        )
