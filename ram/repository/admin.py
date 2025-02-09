from django.contrib import admin

from ram.admin import publish, unpublish
from repository.models import (
    GenericDocument,
    InvoiceDocument,
    BookDocument,
    CatalogDocument,
    DecoderDocument,
    RollingStockDocument
)


@admin.register(GenericDocument)
class GenericDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size", "creation_time", "updated_time")
    list_display = (
        "__str__",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "description",
        "file",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "description",
                    "file",
                    "size",
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


@admin.register(InvoiceDocument)
class InvoiceDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size", "creation_time", "updated_time")
    list_display = (
        "__str__",
        "description",
        "date",
        "shop",
        "size",
        "download",
    )
    search_fields = (
        "rolling_stock__manufacturer__name",
        "rolling_stock__item_number",
        "book__title",
        "catalog__manufacturer__name",
        "shop__name",
        "description",
        "file",
    )
    autocomplete_fields = ("rolling_stock", "book", "catalog", "shop")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "rolling_stock",
                    "book",
                    "catalog",
                    "description",
                    "date",
                    "shop",
                    "file",
                    "size",
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


@admin.register(BookDocument)
class BookDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size",)
    list_display = (
        "__str__",
        "book",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "book__title",
        "description",
        "file",
    )
    autocomplete_fields = ("book",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "book",
                    "description",
                    "file",
                    "size",
                )
            },
        ),
    )
    actions = [publish, unpublish]


@admin.register(CatalogDocument)
class CatalogDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size",)
    list_display = (
        "__str__",
        "catalog",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "catalog__title",
        "description",
        "file",
    )
    autocomplete_fields = ("catalog",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "catalog",
                    "description",
                    "file",
                    "size",
                )
            },
        ),
    )
    actions = [publish, unpublish]


@admin.register(DecoderDocument)
class DecoderDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size",)
    list_display = (
        "__str__",
        "decoder",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "decoder__name",
        "decoder__manufacturer__name",
        "description",
        "file",
    )
    autocomplete_fields = ("decoder",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "decoder",
                    "description",
                    "file",
                    "size",
                )
            },
        ),
    )
    actions = [publish, unpublish]


@admin.register(RollingStockDocument)
class RollingStockDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size",)
    list_display = (
        "__str__",
        "rolling_stock",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "rolling_stock__rolling_class__identifier",
        "rolling_stock__item_number",
        "description",
        "file",
    )
    autocomplete_fields = ("rolling_stock",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "rolling_stock",
                    "description",
                    "file",
                    "size",
                )
            },
        ),
    )
    actions = [publish, unpublish]
