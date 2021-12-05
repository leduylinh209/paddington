from googleads import adwords


CAMPAIGN_ID = '2089990492'
BLOCK_IP = '1.1.1.1'


def add(client, campaign_id, block_ips):
    # Initialize appropriate service.
    campaign_criterion_service = client.GetService('CampaignCriterionService',
                                                   version='v201809')

    # Create campaign criterion with blockd ip
    campaign_criterions = [
        {
            'campaignId': campaign_id,
            'criterion': {
                'xsi_type': 'IpBlock',
                'type': 'IP_BLOCK',
                'ipAddress': ip,
            },
            'xsi_type': 'NegativeCampaignCriterion',
        }
        for ip in block_ips
    ]

    # Create operations.
    operations = [
        {
            'operator': 'ADD',
            'operand': campaign_criterion,
        }
        for campaign_criterion in campaign_criterions
    ]

    # Make the mutate request.
    result = campaign_criterion_service.mutate(operations)

    return [criterion['criterion']['id']
            for criterion in result['value']]


def remove(client, campaign_id, criterion_ids):
    # Initialize appropriate service.
    campaign_criterion_service = client.GetService('CampaignCriterionService',
                                                   version='v201809')

    # Create campaign criterion with blockd ip
    campaign_criterions = [
        {
            'campaignId': campaign_id,
            'criterion': {
                'xsi_type': 'IpBlock',
                'type': 'IP_BLOCK',
                'id': id,
            },
            'xsi_type': 'NegativeCampaignCriterion',
        }
        for id in criterion_ids
    ]

    # Create operations.
    operations = [
        {
            'operator': 'REMOVE',
            'operand': campaign_criterion,
        }
        for campaign_criterion in campaign_criterions
    ]

    # Make the mutate request.
    result = campaign_criterion_service.mutate(operations)

    return [criterion['criterion']['id']
            for criterion in result['value']]


if __name__ == '__main__':
    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage()
    # print(add(adwords_client, CAMPAIGN_ID, [BLOCK_IP]))
    print(remove(adwords_client, CAMPAIGN_ID, [3819388707]))
