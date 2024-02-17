import os
import datetime
import posixpath

from pathlib import Path
from PIL import Image, UnidentifiedImageError

from django.views import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.text import slugify as slugify
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class UploadImage(View):
    def post(self, request, application=None, model=None):
        if not request.user.is_authenticated:
            raise HttpResponseForbidden()

        file_obj = request.FILES["file"]
        file_name, file_extension = os.path.splitext(file_obj.name)
        file_name = slugify(file_name) + file_extension

        try:
            Image.open(file_obj)
        except UnidentifiedImageError:
            response = HttpResponse("Invalid extension")  # FIXME
            response.status_code = 400
            return response

        today = datetime.date.today()
        container = (
            "uploads",
            today.strftime("%Y"),
            today.strftime("%m"),
            today.strftime("%d"),
        )

        file_path = os.path.join(settings.MEDIA_ROOT, *(p for p in container))
        Path(file_path).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(file_path, file_name), "wb+") as f:
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
