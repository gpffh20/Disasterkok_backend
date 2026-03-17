from .base import *  # noqa pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = (
    {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get("POSTGRES_DB"),
            'USER': os.environ.get("POSTGRES_USER"),
            'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
            'HOST': '127.0.0.1',
            'PORT': os.environ.get("POSTGRES_PORT"),
        }
    }
)
