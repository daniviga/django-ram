from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from bookshelf.models import BookProperty, BookImage, Book, Author, Publisher


class BookImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BookImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]


class BookPropertyInline(admin.TabularInline):
    model = BookProperty
    min_num = 0
    extra = 0


@admin.register(Book)
class BookAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (BookImageInline, BookPropertyInline,)
    list_display = (
        "title",
        "get_authors",
        "get_publisher",
        "publication_year",
        "numbers_of_pages"
    )
    search_fields = ("title", "publisher__name", "authors__last_name")
    list_filter = ("publisher__name", "authors")

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
