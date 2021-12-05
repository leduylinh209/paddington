from celery import shared_task
import os
from celery.utils.log import get_task_logger
from googleads import adwords

from service.utils import register_block_ip, deregister_block_ip

logger = get_task_logger(__name__)

# Init google adwords client
adwords_client = adwords.AdWordsClient.LoadFromString("""
adwords:
  developer_token: {developer_token}
  user_agent: Mebaha
  client_customer_id: {client_customer_id}
  client_id: {client_id}
  client_secret: {client_secret}
  refresh_token: {refresh_token}
""".format(
    developer_token=os.getenv("googleads_developer_token"),
    client_customer_id=os.getenv("googleads_client_customer_id"),
    client_id=os.getenv("googleads_client_id"),
    client_secret=os.getenv("googleads_client_secret"),
    refresh_token=os.getenv("googleads_refresh_token"),
))


@shared_task(queue="post_signal")
def send_block_ip_to_google_ads(campaign_id, ip_address):
    from service.ads.models import IpBlock
    try:
        # Batch 100
        for batch in [ip_address[i:i + 100] for i in range(0, len(ip_address), 100)]:
            criterion_ids = register_block_ip(adwords_client, campaign_id, batch)

            for ip, criterion in zip(batch, criterion_ids):
                IpBlock.objects.filter(
                    campaign_id=campaign_id, ip_address=ip
                ).update(
                    is_on=True,
                    criterion_id=criterion,
                )
    except Exception as e:
        logger.error(e)


@shared_task(queue="post_signal")
def remove_block_ip_from_google_ads(campaign_id):
    from service.ads.models import IpBlock
    try:
        criterion_ids = IpBlock.objects.filter(
            campaign_id=campaign_id
        ).values_list(
            'criterion_id', flat=True
        )

        # Batch 100
        for batch in [criterion_ids[i:i + 100] for i in range(0, len(criterion_ids), 100)]:
            criterion_ids = deregister_block_ip(adwords_client, campaign_id, batch)

            for ip, criterion in zip(batch, criterion_ids):
                IpBlock.objects.filter(
                    campaign_id=campaign_id, ip_address=ip
                ).update(
                    is_on=False,
                    criterion_id=criterion,
                )
    except Exception as e:
        logger.error(e)
