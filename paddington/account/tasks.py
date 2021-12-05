import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User

from account.models import Notification
from service.utils import hook_slack, intdot


@shared_task(queue="slack_hook")
def slack_hook_new_signup(user_id):
    url = "http://{}/admin/auth/user/{}/change/".format(
        settings.BASE_HOST,
        user_id,
    )

    user = User.objects.get(id=user_id)
    profile = hasattr(user, 'profile') and user.profile
    name = profile and profile.full_name
    phone = profile and profile.phone
    facebook = profile and profile.personal_facebook
    facebook_link = ""
    if facebook:
        facebook_link = "\nFacebook: {fb}".format(fb=facebook)

    ref_user = profile and profile.referred_by
    ref_profile = hasattr(ref_user, 'profile') and ref_user.profile
    ref_name = ref_profile and ref_profile.full_name
    ref_phone = ref_profile and ref_profile.phone
    ref_facebook = ref_profile and ref_profile.personal_facebook
    ref_facebook_link = ""
    if ref_facebook:
        ref_facebook_link = " - <{fb}|Facebook>".format(fb=ref_facebook)

    fallback = "Mebaha có thành viên mới đăng ký: <{url}|#{id}>".format(
        url=url,
        id=user_id,
    )

    text = """
Họ tên: *{name}* (<tel:{phone}|{phone}>){facebook_link}
Giới thiệu bởi: {ref_name} (<tel:{ref_phone}|{ref_phone}>{ref_facebook_link})
""".format(
        name=name,
        phone=phone,
        facebook_link=facebook_link,
        ref_name=ref_name,
        ref_phone=ref_phone,
        ref_facebook_link=ref_facebook_link,
    )

    attachments = [
        {
            "fallback": fallback,
            "pretext": fallback,
            "color": "#ff759c",
            "text": text,
        }
    ]

    hook_slack("", attachments, settings.SIGNUP_HOOK_URL)


@shared_task(queue="push_noti")
def check_push_notification_result(id):
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic {}".format(settings.ONE_SIGNAL_AUTH_SECRET),
    }
    notification = Notification.objects.get(id=id)
    req = requests.get("https://onesignal.com/api/v1/notifications/{}?app_id={}".format(
        notification.one_signal_id,
        settings.ONE_SIGNAL_APP_ID,
    ), headers=header)
    print(req.status_code, req.reason, req.content)

    if req.status_code == 200:
        result = req.json()
        notification.remaining = result.get("remaining", 0)
        notification.failed = result.get("failed", 0)
        notification.save_without_signals()


@shared_task(queue="push_noti")
def send_push_notification(data):
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic {}".format(settings.ONE_SIGNAL_AUTH_SECRET),
    }

    # Send requests
    if data.get("all_users") is True:
        payload = {
            "app_id": settings.ONE_SIGNAL_APP_ID,
            "included_segments": ["Subscribed Users"],
            "headings": {"en": data["heading"]},
            "contents": {"en": data["content"]},
            "data": data.get("data"),
        }
    else:
        payload = {
            "app_id": settings.ONE_SIGNAL_APP_ID,
            "include_external_user_ids": data["user_id"],
            "headings": {"en": data["heading"]},
            "contents": {"en": data["content"]},
            "data": data.get("data"),
        }

    req = requests.post("https://onesignal.com/api/v1/notifications",
                        headers=header,
                        json=payload)
    print(req.status_code, req.reason, req.content)

    # Save back to notifcation
    if data["notification_id"] is None:
        notification = Notification()
        notification.title = data["heading"]
        notification.content = data["content"]
        notification.type = data["type"]
        notification.object_id = data.get("data") and data["data"].get("id")
        notification.save_without_signals()

        for u in data["user_id"]:
            notification.recipients.add(u)
    else:
        notification = Notification.objects.get(id=data["notification_id"])

    # Update OneSignal id
    if req.status_code == 200:
        result = req.json()
        notification.success = True
        notification.one_signal_id = result["id"]
        notification.one_signal_count = result["recipients"]
    else:
        notification.success = False

    notification.save_without_signals()

    # Check back sending result after 1 minute
    check_push_notification_result.apply_async(args=[notification.id], countdown=60)


def notify_change_balance(transaction):
    change = "tăng" if transaction.amount > 0 else "giảm"
    amount = abs(transaction.amount)
    data = {
        "user_id": [str(transaction.user_id)],
        "heading": "TK vừa {} {} ₫".format(change, intdot(amount)),
        "content": transaction.description,
        "type": "balance",
        "data": {"id": transaction.id, "type": "balance"},
        "notification_id": None,
    }
    send_push_notification.delay(data)


@shared_task(queue="push_noti")
def notify_manually(notification_id):
    # FIXME: Hack to wait for recipients save to db
    notification = Notification.objects.get(id=notification_id)

    data = {
        "user_id": [str(u.id) for u in notification.recipients.all()],
        "heading": notification.title,
        "content": notification.content,
        "type": notification.type,
        "data": {
            "id": notification.object_id,
            "type": notification.type,
            "url": notification.url,
        },
        "notification_id": notification.id,
        "all_users": notification.all_users,
    }

    send_push_notification(data)
