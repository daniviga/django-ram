from django.conf import settings


def default_card_image(request):
    return {"DEFAULT_CARD_IMAGE": settings.DEFAULT_CARD_IMAGE}
