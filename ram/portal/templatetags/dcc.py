from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def dcc(object):
    socket = mark_safe(
        '<i class="bi bi-ban small"></i>'
    )
    decoder = ''
    if object.decoder_interface is not None:
        socket = mark_safe(
            f'<abbr title="{object.get_decoder_interface()}">'
            f'<i class="bi bi-dice-6"></i></abbr>'
        )
    if object.decoder:
        if object.decoder.sound:
            decoder = mark_safe(
                f'<abbr title="{object.decoder}">'
                '<i class="bi bi-volume-up-fill"></i></abbr>'
            )
        else:
            decoder = mark_safe(
                f'<abbr title="{object.decoder}'
                f'({object.get_decoder_interface()})">'
                '<i class="bi bi-cpu-fill"></i></abbr>'
            )
    if decoder:
        return format_html(
            '{} <i class="bi bi-arrow-bar-left"></i> {}',
            socket,
            decoder,
        )

    return socket
