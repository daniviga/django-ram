from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Clear the application cache"

    def handle(self, *args, **options):
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cache cleared"))
        except Exception:
            raise CommandError("Cache is not active")
