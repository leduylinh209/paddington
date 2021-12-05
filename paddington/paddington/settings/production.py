import dj_database_url
import os

from .base import *  # NOQA

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ['mebaha.com']

CELERY_BROKER_URL = 'redis://redis'

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

BASE_HOST = "mebaha.com"
NOIBAICONNECT_BOOKING_URL = "http://api.noibaiconnect.com/api/v1/nbc"
NOIBAICONNECT_BOOKING_STATUS_URL = "http://api.noibaiconnect.com/api/v1/map/track"

ORDER_HOOK_URL = "https://hooks.slack.com/services/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"
SIGNUP_HOOK_URL = "https://hooks.slack.com/services/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"

ONE_SIGNAL_APP_ID = "4fc348c9-ca40-4666-8a21-faeb2a8209d6"
ONE_SIGNAL_AUTH_SECRET = "NWJlOTUyZTUtNDFkOS00MjI5LTllNDUtMmRkNmJhYmUwMmNk"

# Sentry
RAVEN_CONFIG = {
    'dsn': 'https://e08f3da89418463ba7285ddb12f52219:c87c7c75549e4178ad9a77e6cac0ea84@sentry.io/1414406',
    'release': 'production',
}
