from django.conf import settings
from django.apps import AppConfig


class RamConfig(AppConfig):
    name = "ram"

    def ready(self):
        cache_middleware = set([
            "django.middleware.cache.UpdateCacheMiddleware",
            "django.middleware.cache.FetchFromCacheMiddleware",
        ])
        if cache_middleware.issubset(settings.MIDDLEWARE):
            from ram.signals import clear_cache  # noqa: F401
