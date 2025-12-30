from django.conf import settings
from django.contrib import admin
from django.core.cache import cache

admin.site.site_header = settings.SITE_NAME


def publish(modeladmin, request, queryset):
    queryset.update(published=True)
    cache.clear()


publish.short_description = "Publish selected items"


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)
    cache.clear()


unpublish.short_description = "Unpublish selected items"


def set_featured(modeladmin, request, queryset):
    count = queryset.count()
    if count > settings.FEATURED_ITEMS_MAX:
        modeladmin.message_user(
            request,
            "You can only mark up to {} items as featured.".format(
                settings.FEATURED_ITEMS_MAX
            ),
            level="error",
        )
        return
    featured = modeladmin.model.objects.filter(featured=True).count()
    if featured + count > settings.FEATURED_ITEMS_MAX:
        modeladmin.message_user(
            request,
            "There are already {} featured items. You can only mark {} more items as featured.".format(  # noqa: E501
                featured,
                settings.FEATURED_ITEMS_MAX - featured,
            ),
            level="error",
        )
        return
    queryset.update(featured=True)
    cache.clear()


set_featured.short_description = "Mark selected items as featured"


def unset_featured(modeladmin, request, queryset):
    queryset.update(featured=False)
    cache.clear()


unset_featured.short_description = (
    "Unmark selected items as featured"
)
