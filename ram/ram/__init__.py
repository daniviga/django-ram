from django import VERSION as DJANGO_VERSION
from django.utils.termcolors import colorize
from ram.utils import git_suffix

if DJANGO_VERSION < (6, 0):
    exit(
        colorize(
            "ERROR: This project requires Django 6.0 or higher.", fg="red"
        )
    )

__version__ = "0.20.1"
__version__ += git_suffix(__file__)
