from django.db import models
from django.core.exceptions import ValidationError
from ipaddress import IPv4Address, IPv4Network
from solo.models import SingletonModel


class DriverConfiguration(SingletonModel):
    remote_host = models.GenericIPAddressField(
        protocol="IPv4",
        default="192.168.4.1"
    )
    remote_port = models.SmallIntegerField(default=2560)
    timeout = models.SmallIntegerField(default=250)

    network = models.GenericIPAddressField(
        protocol="IPv4",
        default="192.168.4.0",
        blank=True,
        null=True
    )
    subnet_mask = models.GenericIPAddressField(
        protocol="IPv4",
        default="255.255.255.0",
        blank=True,
        null=True
    )

    def __str__(self):
        return "Configuration"

    def clean(self, *args, **kwargs):
        if self.network:
            try:
                IPv4Network(
                    "{0}/{1}".format(self.network, self.subnet_mask))
            except ValueError as e:
                raise ValidationError(e)
        super().clean(*args, **kwargs)

    class Meta:
        verbose_name = "Configuration"
