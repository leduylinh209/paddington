import re
from functools import wraps

import phonenumbers as pn
import pytz
import requests
from django.conf import settings
from django.core.cache import caches
from django.utils.encoding import smart_str
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse

# Default values for cache
DEFAULT_CACHE_ALIAS = 'default'
DEFAULT_CACHE_TIME = 60 * 30  # 30 minutes


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def _smart_key(key):
    return smart_str(
        ''.join([c for c in key if ord(c) > 32 and ord(c) != 127])
    )


def make_key(key, key_prefix, version):
    """
    Truncate all keys to 250 or less and remove control characters, for using
    with memcached
    """
    return ':'.join([key_prefix, str(version), _smart_key(key)])[:250]


def cache_return_wrapper(f=None, cache_time=DEFAULT_CACHE_TIME, except_self=False,
                         cache_alias=DEFAULT_CACHE_ALIAS):
    """
    Just a decorator for cache result of a method
    """
    cache = caches[cache_alias]

    def cache_return_wrapper_inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _args = args[1:] if except_self else args
            cache_key = "{}_{}_{}".format(
                f.__name__,
                str(_args),
                str(frozenset(kwargs.items())),
            )
            cache_value = cache.get(cache_key)
            if not cache_value:
                cache_value = f(*args, **kwargs)
                cache.set(cache_key, cache_value, cache_time)
            return cache_value

        return wrapper
    if f:
        return cache_return_wrapper_inner(f)
    else:
        return cache_return_wrapper_inner


def to_timezone(dt, tz_name=settings.TIME_ZONE):
    """ Convert datetime to timezone datetime

    Args:
        dt (datetime) - The datetime object
        tz_name (str) - The name of timezone

    Returns:
        datetime - The datetime object with new timezone, invalid timezone
                   name make no effect

    """
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return dt

    return dt.astimezone(tz)


def format_date_time_zone(dt, f="%d/%m/%Y %H:%M:%S"):
    """
    Format datetime using TIME_ZONE in settings
    """
    try:
        return to_timezone(dt, settings.TIME_ZONE).strftime(f)
    except Exception:
        return dt


def hook_slack(message, attachments, hook_url):
    req = {
        "text": message,
        "icon_emoji": ":ghost:",
        "mrkdwn": True,
        "attachments": attachments,
    }

    try:
        requests.post(hook_url, json=req, timeout=5)
    except Exception:
        pass


def intdot(value):
    """
    Convert an integer to a string containing commas every three digits.
    For example, 3000 becomes '3.000' and 45000 becomes '45.000'.
    """
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>.\g<2>', orig)
    if orig == new:
        return new
    else:
        return intdot(new)


def standardize_phone_number(phone):
    """
    Return a phone number having format like: 0973210909.
      + Have a leading zero
      + No spaces/tabs, periods, dashes and parentheses.
      + No national code: +84
    """

    try:
        phone_number = pn.parse(phone, 'VN')
        if pn.is_valid_number(phone_number):
            return pn.format_number(
                phone_number, pn.PhoneNumberFormat.NATIONAL
            ).replace(' ', '')
        else:
            return None

    except pn.phonenumberutil.NumberParseException:
        return None


def register_block_ip(client, campaign_id, block_ips):
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


def deregister_block_ip(client, campaign_id, criterion_ids):
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


def hook_telegram(message):
    url = "https://api.telegram.org/bot968092526:AAHTvrnW9FSwRx9Z60mJq4mtPOJ_gBbnQlc/sendMessage?chat_id=-1001197185830&parse_mode=markdown&text={message}".format(
        message=urllib.parse.quote(message)
    )
    requests.get(url)
