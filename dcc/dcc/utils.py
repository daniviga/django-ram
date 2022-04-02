from django.utils.html import format_html
from django.utils.text import slugify as django_slugify


def get_image_preview(url):
    return format_html(
        '<img src="%s" style="max-width: 150px; max-height: 150px;'
        'background-color: #eee;" />' % url
    )


def slugify(string, custom_separator=None):
    # Make slug 'flat', both '-' and '_' are replaced with '-'
    string = django_slugify(string).replace("_", "-")
    if custom_separator is not None:
        string = string.replace("-", custom_separator)
    return string
