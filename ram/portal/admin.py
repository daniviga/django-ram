from django.contrib import admin
from solo.admin import SingletonModelAdmin

from portal.models import SiteConfiguration, Flatpage


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
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
                    "footer",
                    "footer_extended",
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
