from django.utils.html import format_html


def get_image_preview(url):
    return format_html(
        '<img src="%s" style="max-width: 150px; max-height: 150px;'
        'background-color: #eee;" />' % url)
