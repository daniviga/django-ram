from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def dynamic_admin_url(app_name, model_name, object_id=None):
    if object_id:
        return reverse(
            f'admin:{app_name}_{model_name}_change',
            args=[object_id]
        )
    return reverse(f'admin:{app_name}_{model_name}_changelist')


@register.simple_tag
def dynamic_pagination(reverse_name, page):
    if reverse_name.endswith('y'):
        return reverse(f'{reverse_name[:-1]}ies_pagination', args=[page])
    return reverse(f'{reverse_name}s_pagination', args=[page])
