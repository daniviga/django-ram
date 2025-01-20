from django.core.cache import cache
from django.utils.cache import add_never_cache_headers, get_cache_key


class DisableClientSideCachingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the cache key exists for this request
        cache_key = get_cache_key(request)
        cache_hit = "MISS"
        if cache_key and cache.get(cache_key):
            cache_hit = "HIT"
        response['X-Cache-Hit'] = cache_hit

        add_never_cache_headers(response)
        return response
