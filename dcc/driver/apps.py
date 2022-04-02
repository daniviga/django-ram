from django.apps import AppConfig
from health_check.plugins import plugin_dir


class DriverConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "driver"

    def ready(self):
        from driver.health import DriverHealthCheck

        plugin_dir.register(DriverHealthCheck)
