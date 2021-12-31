from django.db import models
from solo.models import SingletonModel


class DriverConfiguration(SingletonModel):
    remote_host = models.GenericIPAddressField(
        protocol="IPv4", default="192.168.4.1")
    remote_port = models.SmallIntegerField(default=2560)

    def __str__(self):
        return "Driver Configuration"

    class Meta:
        verbose_name = "Driver Configuration"
