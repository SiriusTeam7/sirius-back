"""
WSGI config for sirius project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from dj_static import Cling
from configurations.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sirius.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Development")

application = Cling(get_wsgi_application())
