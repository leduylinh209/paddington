from django.db import models
from paddington.models import TrackingAbstractModel


class AppRelease(TrackingAbstractModel):
    version = models.CharField(max_length=32)
    release_note = models.TextField()
    stores = models.CharField(max_length=64, db_index=True)
