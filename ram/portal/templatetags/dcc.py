from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def dcc(object):
    socket = (
        '<i class="bi bi-ban small"></i>'
    )
    decoder = ''
    if object.decoder_interface is not None:
        socket = (
            f'<abbr title="{object.get_decoder_interface()}">'
            f'<i class="bi bi-dice-6"></i></abbr>'
        )
    if object.decoder:
        if object.decoder.sound:
            decoder = (
                f'<abbr title="{object.decoder} (with sounds)">'
                '<i class="bi bi-volume-up-fill"></i></abbr>'
            )
        else:
            decoder = (
                f'<abbr title="{object.decoder}">'
                '<i class="bi bi-cpu-fill"></i></abbr>'
            )

    if decoder:
        return format_html(
            f'{socket} <i class="bi bi-arrow-bar-left"></i> {decoder}'
        )

    return format_html(socket)
