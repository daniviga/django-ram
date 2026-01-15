"""
Django settings for ram project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-ram-insecure-Chang3m3-1n-Pr0duct10n!"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "adminsortable2",
    "django_countries",
    "solo",
    "tinymce",
    "rest_framework",
    "ram",
    "portal",
    # "driver",  # uncomment this to enable the "driver" API
    "metadata",
    "repository",
    "roster",
    "consist",
    "bookshelf",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.context_processors.default_card_image",
            ],
        },
    },
]

WSGI_APPLICATION = "ram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": STORAGE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "media/"
MEDIA_ROOT = STORAGE_DIR / "media"

# cookies hardening
SESSION_COOKIE_NAME = '__Secure-sessionid'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_NAME = '__Secure-csrftoken'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# django-ram REST API settings
REST_ENABLED = False  # Set to True to enable the REST API
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",  # noqa: E501
    "PAGE_SIZE": 5,
}

TINYMCE_DEFAULT_CONFIG = {
    "height": "300px",
    "menubar": False,
    "plugins": "autolink lists link image charmap preview anchor "
    "searchreplace visualblocks code fullscreen insertdatetime media "
    "table paste code",
    "toolbar": "undo redo | "
    "bold italic underline strikethrough removeformat | "
    "fontsizeselect formatselect | "
    "alignleft aligncenter alignright alignjustify | "
    "outdent indent numlist bullist | "
    "insertfile image media pageembed template link anchor codesample | "
    "charmap | "
    "fullscreen preview code",
    "images_upload_url": "/tinymce/upload_image",
}

COUNTRIES_OVERRIDE = {
    "EU": "Europe",
    "XX": "None",
}

SITE_NAME = "Railroad Assets Manager"

# Image used on cards without a custom image uploaded.
# The file must be placed in the root of the 'static' folder
DEFAULT_CARD_IMAGE = "coming_soon.svg"

# Second level ALT separator for CSV files (e.g. for properties)
CSV_SEPARATOR_ALT = ";"

DECODER_INTERFACES = [
    (0, "Built-in"),
    (1, "NEM651"),
    (2, "NEM652"),
    (3, "NEM658 (Plux16)"),
    (6, "NEM658 (Plux22)"),
    (4, "NEM660 (21MTC)"),
    (5, "NEM662 (Next18/Next18S)"),
]

MANUFACTURER_TYPES = [
    ("model", "Model"),
    ("real", "Real"),
    ("accessory", "Accessory"),
    ("other", "Other")
]

ROLLING_STOCK_TYPES = [
    ("engine", "Engine"),
    ("car", "Car"),
    ("railcar", "Railcar"),
    ("equipment", "Equipment"),
    ("other", "Other"),
]

FEATURED_ITEMS_MAX = 6

# If True, use X-Accel-Redirect (Nginx)
# when using X-Accel-Redirect, we don't serve the file
# directly from Django, but let Nginx handle it
# in Nginx config, we need to map /private/ to
# the actual media files location with internal directive
# eg:
#   location /private {
#       internal;
#       alias /path/to/media;
#   }
# make also sure that the entire /media is _not_ mapped directly in Nginx
USE_X_ACCEL_REDIRECT = False

try:
    from ram.local_settings import *
except ImportError:
    # If a local_setting.py does not exist
    # settings in this file only will be used
    pass
