import os
import datetime
import posixpath

from pathlib import Path
from PIL import Image, UnidentifiedImageError

from django.views import View
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils.text import slugify as slugify
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 25


@method_decorator(csrf_exempt, name="dispatch")
class UploadImage(View):
    def post(self, request):
        if not request.user.is_authenticated:
            raise HttpResponseForbidden()

        file_obj = request.FILES["file"]
        file_name, file_extension = os.path.splitext(file_obj.name)
        file_name = slugify(file_name) + file_extension

        try:
            Image.open(file_obj)
        except UnidentifiedImageError:
            return HttpResponseBadRequest()

        today = datetime.date.today()
        container = (
            "uploads",
            today.strftime("%Y"),
            today.strftime("%m"),
            today.strftime("%d"),
        )

        dir_path = os.path.join(settings.MEDIA_ROOT, *(p for p in container))
        file_path = os.path.normpath(os.path.join(dir_path, file_name))
        # even if we apply slugify to the file name, add more hardening
        # to avoid any path transversal risk
        if not file_path.startswith(str(settings.MEDIA_ROOT)):
            return HttpResponseBadRequest()

        Path(dir_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb+") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

            return JsonResponse(
                {
                    "message": "Image uploaded successfully",
                    "location": posixpath.join(
                        settings.MEDIA_URL, *(p for p in container), file_name
                    ),
                }
            )
