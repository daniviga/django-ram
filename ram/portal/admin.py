from django.conf import settings
from django.contrib import admin
from solo.admin import SingletonModelAdmin
from tinymce.widgets import TinyMCE

from ram.admin import publish, unpublish
from portal.models import SiteConfiguration, Flatpage


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    readonly_fields = ("site_name", "rest_api", "version")
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
                    "featured_items_ordering",
                    "currency",
                    "footer",
                    "footer_extended",
                    "disclaimer",
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
                    "rest_api",
                    "version",
                ),
            },
        ),
    )

    @admin.display(description="REST API enabled", boolean=True)
    def rest_api(self, obj):
        return settings.REST_ENABLED

    @admin.display()
    def version(self, obj):
        return "{} (Django {})".format(obj.version, obj.django_version)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ("footer", "footer_extended", "disclaimer"):
            return db_field.formfield(
                widget=TinyMCE(
                    mce_attrs={"height": "200"},
                )
            )
        return super().formfield_for_dbfield(db_field, **kwargs)


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
