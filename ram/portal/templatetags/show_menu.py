from django import template
from portal.models import Flatpage
from bookshelf.models import Book

register = template.Library()


@register.inclusion_tag('bookshelf_menu.html')
def show_bookshelf_menu():
    return {"bookshelf_menu": Book.objects.exists()}


@register.inclusion_tag('flatpage_menu.html')
def show_flatpage_menu():
    menu = Flatpage.objects.filter(published=True).order_by("name")
    return {"flatpage_menu": menu}
