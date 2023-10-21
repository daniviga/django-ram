from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def clear_cache(sender, **kwargs):
    cache.clear()
