from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from bookshelf.models import (
    BaseBookProperty,
    BaseBookImage,
    BaseBookDocument,
    Book,
    Author,
    Publisher,
    Catalog,
)


class BookImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseBookImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]
    verbose_name = "Image"


class BookDocInline(admin.TabularInline):
    model = BaseBookDocument
    min_num = 0
    extra = 0
    classes = ["collapse"]


class BookPropertyInline(admin.TabularInline):
    model = BaseBookProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)
    verbose_name = "Property"
    verbose_name_plural = "Properties"


@admin.register(Book)
class BookAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        BookDocInline,
    )
    list_display = (
        "title",
        "get_authors",
        "get_publisher",
        "publication_year",
        "number_of_pages",
        "published",
    )
    autocomplete_fields = ("authors", "publisher")
    readonly_fields = ("creation_time", "updated_time")
    search_fields = ("title", "publisher__name", "authors__last_name")
    list_filter = ("publisher__name", "authors")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "title",
                    "authors",
                    "publisher",
                    "ISBN",
                    "language",
                    "number_of_pages",
                    "publication_year",
                    "description",
                    "purchase_date",
                    "notes",
                    "tags",
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

    @admin.display(description="Publisher")
    def get_publisher(self, obj):
        return obj.publisher.name

    @admin.display(description="Authors")
    def get_authors(self, obj):
        return ", ".join(a.short_name() for a in obj.authors.all())


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = ("last_name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)


@admin.register(Catalog)
class CatalogAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        BookDocInline,
    )
    list_display = (
        "__str__",
        "manufacturer",
        "years",
        "get_scales",
        "published",
    )
    autocomplete_fields = ("manufacturer",)
    readonly_fields = ("creation_time", "updated_time")
    search_fields = ("manufacturer__name", "years", "scales__scale")
    list_filter = ("manufacturer__name", "publication_year", "scales__scale")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "manufacturer",
                    "years",
                    "scales",
                    "ISBN",
                    "language",
                    "number_of_pages",
                    "publication_year",
                    "description",
                    "purchase_date",
                    "notes",
                    "tags",
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

    @admin.display(description="Scales")
    def get_scales(self, obj):
        return "/".join(s.scale for s in obj.scales.all())
