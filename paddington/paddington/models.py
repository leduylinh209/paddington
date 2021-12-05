from django.db import models
from django.contrib.auth.models import User


class SignalSaveMixin(object):

    def save_without_signals(self, *args, **kwargs):
        self._disable_signals = True
        self.save(*args, **kwargs)
        self._disable_signals = False


class CreatedAbstractModel(models.Model):

    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        editable=False
    )

    created_at = models.DateTimeField(
        "Created at",
        blank=True,
        null=True,
        auto_now_add=True,
        db_index=True,
        editable=False,
    )

    class Meta:
        abstract = True


class ModifiedAbstractModel(models.Model):

    modified_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_modified',
        editable=False
    )

    modified_at = models.DateTimeField(
        "Modified at",
        blank=True,
        null=True,
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True


class TrackingAbstractModel(CreatedAbstractModel,
                            ModifiedAbstractModel,
                            SignalSaveMixin):

    class Meta:
        abstract = True

    def __str__(self):
        return "{} #{}".format(self.__class__.__name__, self.id)
