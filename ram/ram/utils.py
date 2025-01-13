import os
import csv
import hashlib
import subprocess

from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.text import slugify as django_slugify
from django.core.files.storage import FileSystemStorage


class DeduplicatedStorage(FileSystemStorage):
    """
    A derived FileSystemStorage class that compares already existing files
    (with the same name) with new uploaded ones and stores new file only if
    sha256 hash on is content is different
    """

    def save(self, name, content, max_length=None):
        if super().exists(name):
            new = hashlib.sha256(content.read()).hexdigest()
            with open(super().path(name), "rb") as file:
                file_binary = file.read()
                old = hashlib.sha256(file_binary).hexdigest()
            if old == new:
                return name

        return super().save(name, content, max_length)


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


def get_image_preview(url, max_size=150):
    return format_html(
        '<img src="{src}" style="max-width: {size}px; max-height: {size}px;'
        'background-color: #eee;" />'.format(src=url, size=max_size)
    )


def slugify(string, custom_separator=None):
    # Make slug 'flat', both '-' and '_' are replaced with '-'
    string = django_slugify(string).replace("_", "-")
    if custom_separator is not None:
        string = string.replace("-", custom_separator)
    return string


def generate_csv(header, data, filename):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(
        filename
    )
    writer = csv.writer(response)
    writer.writerow(header)
    for row in data:
        writer.writerow(row)
    return response
