"""
WSGI config for paddington project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from newrelic import agent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddington.settings')

agent.initialize('newrelic.ini')

application = agent.WSGIApplicationWrapper(get_wsgi_application())
