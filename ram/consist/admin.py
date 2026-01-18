import html

from django.conf import settings
from django.contrib import admin

# from django.forms import BaseInlineFormSet  # for future reference
from django.utils.html import format_html, strip_tags
from adminsortable2.admin import (
    SortableAdminBase,
    SortableInlineAdminMixin,
    # CustomInlineFormSetMixin,  # for future reference
)

from ram.admin import publish, unpublish
from ram.utils import generate_csv
from consist.models import Consist, ConsistItem


# for future reference
# class ConsistItemInlineFormSet(CustomInlineFormSetMixin, BaseInlineFormSet):
#     def clean(self):
#         super().clean()


class ConsistItemInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ConsistItem
    min_num = 1
    extra = 0
    autocomplete_fields = ("rolling_stock",)
    readonly_fields = (
        "preview",
        "published",
        "scale",
        "manufacturer",
        "item_number",
        "company",
        "type",
        "era",
        "address",
    )


@admin.register(Consist)
class ConsistAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (ConsistItemInline,)
    readonly_fields = (
        "creation_time",
        "updated_time",
    )
    list_filter = ("published", "company__name", "era", "scale__scale")
    list_display = (
        "__str__",
        "company__name",
        "era",
        "scale",
        "country_flag",
        "published",
    )
    search_fields = ("identifier",) + list_filter
    save_as = True

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        qs = super().get_queryset(request)
        return qs.with_related()

    @admin.display(description="Country")
    def country_flag(self, obj):
        return format_html(
            '<img src="{}" title="{}" />', obj.country.flag, obj.country.name
        )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "identifier",
                    "company",
                    "scale",
                    "era",
                    "consist_address",
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

    def download_csv(modeladmin, request, queryset):
        header = [
            "ID",
            "Name",
            "Published",
            "Company",
            "Country",
            "Address",
            "Scale",
            "Era",
            "Description",
            "Tags",
            "Length",
            "Composition",
            "Item name",
            "Item type",
            "Item ID",
        ]
        data = []

        # Prefetch related data to avoid N+1 queries
        queryset = queryset.select_related(
            'company', 'scale'
        ).prefetch_related(
            'tags',
            'consist_item__rolling_stock__rolling_class__type'
        )

        for obj in queryset:
            # Cache the type count to avoid recalculating for each item
            types = " + ".join(
                "{}x {}".format(t["count"], t["type"])
                for t in obj.get_type_count()
            )
            # Cache tags to avoid repeated queries
            tags_str = settings.CSV_SEPARATOR_ALT.join(
                t.name for t in obj.tags.all()
            )

            for item in obj.consist_item.all():
                data.append(
                    [
                        obj.uuid,
                        obj.__str__(),
                        "X" if obj.published else "",
                        obj.company.name,
                        obj.company.country,
                        obj.consist_address,
                        obj.scale.scale,
                        obj.era,
                        html.unescape(strip_tags(obj.description)),
                        tags_str,
                        obj.length,
                        types,
                        item.rolling_stock.__str__(),
                        item.type,
                        item.rolling_stock.uuid,
                    ]
                )

        return generate_csv(header, data, "consists.csv")

    download_csv.short_description = "Download selected items as CSV"

    actions = [publish, unpublish, download_csv]
