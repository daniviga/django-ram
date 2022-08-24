from django import template
from portal.views import Flatpage

register = template.Library()


@register.inclusion_tag('flatpage_menu.html')
def show_menu():
    menu = Flatpage.objects.all()
    return {"menu": menu}
