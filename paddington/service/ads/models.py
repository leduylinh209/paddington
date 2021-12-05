from django.db import models
from model_utils.models import TimeStampedModel


class IpBlock(TimeStampedModel):
    """
    Model to block ip in campaign
    """
    campaign_id = models.CharField(max_length=32, editable=False)
    ip_address = models.CharField(max_length=256, editable=False)
    is_on = models.BooleanField(default=False, editable=False)
    criterion_id = models.BigIntegerField(null=True, editable=False)

    class Meta:
        unique_together = (('campaign_id', 'ip_address'),)

    def __str__(self):
        return "Block ip {} for campaign {}".format(self.ip_address, self.campaign_id)
