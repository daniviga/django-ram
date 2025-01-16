from django.conf import settings
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from ram.admin import publish, unpublish
from portal.models import SiteConfiguration, Flatpage


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    readonly_fields = ("site_name", "rest_api")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "site_name",
                    "site_author",
                    "about",
                    "items_per_page",
                    "items_ordering",
                    "currency",
                    "footer",
                    "footer_extended",
                    "rest_api",
                )
            },
        ),
        (
            "Advanced",
            {
                "classes": ("collapse",),
                "fields": (
                    "show_version",
                    "use_cdn",
                    "extra_head",
                ),
            },
        ),
    )

    @admin.display(description="REST API enabled", boolean=True)
    def rest_api(self, obj):
        return settings.REST_ENABLED


@admin.register(Flatpage)
class FlatpageAdmin(admin.ModelAdmin):
    readonly_fields = ("path", "creation_time", "updated_time")
    list_display = ("name", "path", "published", "get_link")
    list_filter = ("published",)
    search_fields = ("name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "path",
                    "content",
                    "published",
                )
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": (
                    "creation_time",
                    "updated_time",
                ),
            },
        ),
    )
    actions = [publish, unpublish]
