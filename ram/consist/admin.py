from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from ram.admin import publish, unpublish
from consist.models import Consist, ConsistItem


class ConsistItemInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ConsistItem
    min_num = 1
    extra = 0
    autocomplete_fields = ("rolling_stock",)
    readonly_fields = (
        "preview",
        "published",
        "address",
        "type",
        "company",
        "era",
    )


@admin.register(Consist)
class ConsistAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (ConsistItemInline,)
    readonly_fields = (
        "creation_time",
        "updated_time",
    )
    list_filter = ("company", "era", "published")
    list_display = ("__str__",) + list_filter + ("country_flag",)
    search_fields = ("identifier",) + list_filter
    save_as = True

    @admin.display(description="Country")
    def country_flag(self, obj):
        return format_html(
            '<img src="{}" /> {}'.format(obj.country.flag, obj.country)
        )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "identifier",
                    "consist_address",
                    "company",
                    "era",
                    "description",
                    "image",
                    "tags",
                )
            },
        ),
        (
            "Notes",
            {"classes": ("collapse",), "fields": ("notes",)},
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
