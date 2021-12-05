from django.contrib import admin
from service.ads.models import IpBlock
from paddington.admin import TrackingAdminMixin, ReadOnlyAdminMixin


@admin.register(IpBlock)
class IpBlockAdmin(ReadOnlyAdminMixin, TrackingAdminMixin):
    list_display = readonly_fields = ['id', 'campaign_id', 'ip_address', 'is_on',
                                      'criterion_id', 'created']
