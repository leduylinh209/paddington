import dj_database_url

from .base import *  # NOQA

ALLOWED_HOSTS = ["*"]

CELERY_BROKER_URL = "redis://redis"

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# CORS_REPLACE_HTTPS_REFERER = True

BASE_HOST = "mebaha.com"

# Sentry
RAVEN_CONFIG = {
    "dsn": "https://e08f3da89418463ba7285ddb12f52219:c87c7c75549e4178ad9a77e6cac0ea84@sentry.io/1414406",
    "release": "develop",
}
