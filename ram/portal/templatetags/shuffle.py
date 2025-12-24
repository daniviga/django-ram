import random
from django import template

register = template.Library()


@register.filter
def shuffle(items):
    shuffled_items = list(items)
    random.shuffle(shuffled_items)
    return shuffled_items
