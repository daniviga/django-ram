from django import template
from portal.models import Flatpage
from bookshelf.models import Book, Catalog, Magazine

register = template.Library()


@register.inclusion_tag('bookshelf/bookshelf_menu.html')
def show_bookshelf_menu():
    # FIXME: Filter out unpublished books and catalogs?
    books = Book.objects.exists()
    catalogs = Catalog.objects.exists()
    magazines = Magazine.objects.exists()
    return {
        "bookshelf_menu": (books or catalogs or magazines),
        "books_menu": books,
        "catalogs_menu": catalogs,
        "magazines_menu": magazines,
    }


@register.inclusion_tag('flatpages/flatpages_menu.html')
def show_flatpages_menu(user):
    menu = Flatpage.objects.get_published(user).order_by("name")
    return {"flatpages_menu": menu}
