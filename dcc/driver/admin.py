from django.contrib import admin
from solo.admin import SingletonModelAdmin

from driver.models import DriverConfiguration


@admin.register(DriverConfiguration)
class DriverConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            "Remote DCC-EX configuration",
            {
                "fields": (
                    "remote_host",
                    "remote_port",
                    "timeout",
                )
            },
        ),
        (
            "Firewall setting",
            {
                "fields": (
                    "network",
                    "subnet_mask",
                )
            },
        ),
    )
