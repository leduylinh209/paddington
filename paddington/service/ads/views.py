from rest_framework import views
from rest_framework.response import Response
from service.ads.models import IpBlock
from service.ads.tasks import send_block_ip_to_google_ads, remove_block_ip_from_google_ads


class BlockIPView(views.APIView):

    def post(self, request, *args, **kwargs):
        campaign_id = request.data.get('campaign_id')
        ip_address = request.data.get('ip_address')

        if type(ip_address) is not list:
            ip_address = [ip_address]

        for ip in ip_address:
            IpBlock.objects.get_or_create(
                campaign_id=campaign_id,
                ip_address=ip,
            )
        send_block_ip_to_google_ads.delay(campaign_id, ip_address)
        return Response({"ack": True})


class UnblockIPView(views.APIView):

    def post(self, request, *args, **kwargs):
        campaign_id = request.data.get('campaign_id')
        remove_block_ip_from_google_ads.delay(campaign_id)
        return Response({"ack": True})


block_ip = BlockIPView.as_view()
unblock_ip = UnblockIPView.as_view()
