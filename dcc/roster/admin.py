from django.contrib import admin
from roster.models import (
    RollingClass,
    RollingClassProperty,
    RollingStock,
    RollingStockImage,
    RollingStockDocument,
    RollingStockProperty,
)


class RollingClassPropertyInline(admin.TabularInline):
    model = RollingClassProperty
    min_num = 0
    extra = 0


@admin.register(RollingClass)
class RollingClass(admin.ModelAdmin):
    inlines = (RollingClassPropertyInline,)
    list_display = ("__str__", "type", "company")
    list_filter = ("company", "type__category", "type")
    search_fields = list_display


class RollingStockDocInline(admin.TabularInline):
    model = RollingStockDocument
    min_num = 0
    extra = 0


class RollingStockImageInline(admin.TabularInline):
    model = RollingStockImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)


class RollingStockPropertyInline(admin.TabularInline):
    model = RollingStockProperty
    min_num = 0
    extra = 0


@admin.register(RollingStock)
class RollingStockAdmin(admin.ModelAdmin):
    inlines = (
        RollingStockPropertyInline,
        RollingStockImageInline,
        RollingStockDocInline,
    )
    readonly_fields = ("creation_time", "updated_time")
    list_display = (
        "__str__",
        "address",
        "manufacturer",
        "scale",
        "sku",
        "company",
        "country",
    )
    list_filter = (
        "rolling_class__type__category",
        "rolling_class__type",
        "scale",
        "manufacturer",
    )
    search_fields = list_display

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "rolling_class",
                    "road_number",
                    "scale",
                    "manufacturer",
                    "sku",
                    "era",
                    "production_year",
                    "purchase_date",
                    "notes",
                    "tags",
                )
            },
        ),
        (
            "DCC",
            {
                "fields": (
                    "decoder",
                    "address",
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
