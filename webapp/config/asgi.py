"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from pathlib import Path

import dotenv

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

dotenv.read_dotenv(
    Path(__file__).resolve().parent.parent / '.env'
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

from notification.middleware import JWTAuthMiddlewareStack
from notification.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
