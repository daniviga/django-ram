from django import template
from portal.models import Flatpage
from bookshelf.models import Book

register = template.Library()


@register.inclusion_tag('bookshelf/bookshelf_menu.html')
def show_bookshelf_menu():
    return {"bookshelf_menu": Book.objects.exists()}


@register.inclusion_tag('flatpages/flatpages_menu.html')
def show_flatpages_menu(user):
    menu = Flatpage.objects.get_published(user).order_by("name")
    return {"flatpages_menu": menu}
