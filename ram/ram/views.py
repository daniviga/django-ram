import os
import datetime
import posixpath

from pathlib import Path
from PIL import Image, UnidentifiedImageError

from django.apps import apps
from django.conf import settings
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    FileResponse,
    JsonResponse,
)
from django.views import View
from django.utils.text import slugify as slugify
from django.utils.encoding import smart_str
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.pagination import LimitOffsetPagination

from ram.models import PrivateDocument


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


class DownloadFile(View):
    def get(self, request, filename):
        # Clean up the filename to prevent directory traversal attacks
        filename = os.path.basename(filename)

        # Find a document where the stored file name matches
        # Find all models inheriting from PublishableFile
        for model in apps.get_models():
            if issubclass(model, PrivateDocument) and not model._meta.abstract:
                try:
                    doc = model.objects.get(file__endswith=filename)
                    if doc.private and not request.user.is_staff:
                        raise Http404("File not found")

                    file_path = doc.file.path
                    if not os.path.exists(file_path):
                        raise Http404("File not found")

                    response = FileResponse(open(file_path, "rb"), as_attachment=True)
                    response["Content-Disposition"] = (
                        f'attachment; filename="{smart_str(os.path.basename(file_path))}"'
                    )
                    return response
                except model.DoesNotExist:
                    continue

        raise Http404("File not found")
