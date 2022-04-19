import os
import subprocess

from django.utils.html import format_html
from django.utils.text import slugify as django_slugify


def git_suffix(fname):
    """
    :returns: `<short git hash>` if Git repository found
    """
    try:
        gh = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=open(os.devnull, "w"),
        ).strip()
        gh = "-git" + gh.decode() if gh else ""
    except Exception:
        # trapping everything on purpose; git may not be installed or it
        # may not work properly
        gh = ""

    return gh


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
