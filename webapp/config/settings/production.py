from .base import *  # noqa pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB"),
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("POSTGRES_HOST", "db"),
        'PORT': os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# STATIC_ROOT = PROJECT_DIR / 'static'
# MEDIA_ROOT = PROJECT_DIR / 'media'