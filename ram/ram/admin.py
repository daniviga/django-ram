from django.contrib import admin
from django.conf import settings

admin.site.site_header = settings.SITE_NAME


def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.published = True
        obj.save()


publish.short_description = "Publish selected items"


def unpublish(modeladmin, request, queryset):
    for obj in queryset:
        obj.published = False
        obj.save()


unpublish.short_description = "Unpublish selected items"
