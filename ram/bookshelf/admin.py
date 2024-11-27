from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from bookshelf.models import (
    BaseBookProperty, BaseBookImage, Book, Author, Publisher
)


class BookImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseBookImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]


class BookPropertyInline(admin.TabularInline):
    model = BaseBookProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)


@admin.register(Book)
class BookAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (BookImageInline, BookPropertyInline,)
    list_display = (
        "title",
        "published",
        "get_authors",
        "get_publisher",
        "publication_year",
        "number_of_pages"
    )
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
    search_fields = ("first_name", "last_name",)
    list_filter = ("last_name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
