from django import template
from portal.models import Flatpage
from bookshelf.models import Book, Catalog

register = template.Library()


@register.inclusion_tag('bookshelf/bookshelf_menu.html')
def show_bookshelf_menu():
    # FIXME: Filter out unpublished books and catalogs?
    return {
        "bookshelf_menu": (Book.objects.exists() or Catalog.objects.exists()),
        "books_menu": Book.objects.exists(),
        "catalogs_menu": Catalog.objects.exists(),
    }


@register.inclusion_tag('flatpages/flatpages_menu.html')
def show_flatpages_menu(user):
    menu = Flatpage.objects.get_published(user).order_by("name")
    return {"flatpages_menu": menu}
