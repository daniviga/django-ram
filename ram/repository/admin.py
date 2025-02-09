from django.contrib import admin

from ram.admin import publish, unpublish
from repository.models import (
    GenericDocument,
    BaseBookDocument,
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


# @admin.register(BaseBookDocument)
# class BookDocumentAdmin(admin.ModelAdmin):
#     readonly_fields = ("size",)
#     list_display = (
#         "__str__",
#         # FIXME
#         "book__book",
#         "book__catalog",
#         "description",
#         "private",
#         "size",
#         "download",
#     )
#     search_fields = (
#         "book__title",
#         "description",
#         "file",
#     )
#     fieldsets = (
#         (
#             None,
#             {
#                 "fields": (
#                     "private",
#                     # FIXME
#                     "description",
#                     "file",
#                     "size",
#                 )
#             },
#         ),
#     )
#     actions = [publish, unpublish]


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
