import os
import re
import zipfile
from collections import defaultdict

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User

from account.models import (Communication, CommunicationResponse,
                            CommunicationStatus, CommunicationType)
from account.tasks import send_push_notification
from service.merchandise.models import Image, Product
from service.utils import hook_slack, intdot, hook_telegram


@shared_task(queue="slack_hook")
def slack_hook_new_order(booking_data):
    url = "http://{}/admin/merchandise/order/{}/change/".format(
        settings.BASE_HOST,
        booking_data["id"],
    )

    created_by = User.objects.get(id=booking_data["created_by"])
    profile = hasattr(created_by, 'profile') and created_by.profile

    user_name = (created_by.last_name + " " + created_by.first_name) or created_by.username
    user_phone = profile and profile.phone
    personal_facebook = profile and profile.personal_facebook

    profile_link = "<http://{}/admin/auth/user/{}/change/|Profile>".format(
        settings.BASE_HOST,
        created_by.id,
    )

    facebook_link_text = ""
    if personal_facebook:
        facebook_link_text = " - <{}|Facebook>".format(personal_facebook)

    fallback = "Đơn hàng mới vừa được tạo: <{url}|#{id}>".format(
        url=url,
        id=booking_data["id"],
    )

    collect_on_behalf_text = ""
    if booking_data["collect_on_behalf"]:
        collect_on_behalf_text = "\nSố tiền thu hộ: *{}* ₫".format(intdot(booking_data["collection_money"]))

    delivery_note_text = ""
    if booking_data["delivery_note"]:
        delivery_note_text = "\nLưu ý: {}".format(booking_data["delivery_note"])

    shipping_cost_included_text = "Có" if booking_data["shipping_cost_included"] is True else "Không"

    text = """
*{product_name}*
Số lượng: *{quantity}*. Thành tiền: *{amount}* ₫{collect_on_behalf}
Đối tác: {user_name} (<tel:{user_phone}|{user_phone}> - {profile_link}{facebook_link}){delivery_note}
Khách hàng thanh toán phí ship: {shipping_cost_included}
Người nhận: {receiver_name} (<tel:{receiver_phone}|{receiver_phone}>)
Địa chỉ: {receiver_address}
""".format(
        user_name=user_name,
        user_phone=user_phone,
        product_name=booking_data["product_name"],
        shipping_cost_included=shipping_cost_included_text,
        receiver_name=booking_data["receiver_name"],
        receiver_phone=booking_data["receiver_phone"],
        receiver_address=booking_data["receiver_address"],
        quantity=booking_data["quantity"],
        amount=intdot(booking_data["amount"]),
        profile_link=profile_link,
        facebook_link=facebook_link_text,
        collect_on_behalf=collect_on_behalf_text,
        delivery_note=delivery_note_text,
    )

    attachments = [
        {
            "fallback": fallback,
            "pretext": fallback,
            "color": "#ff759c",
            "text": text,
        }
    ]

    hook_slack("", attachments, settings.ORDER_HOOK_URL)

    # Hook telegram
    telegram_text = """
🙌🏻 *Có đơn hàng mới từ CTV Mebaha* 🙌🏻

Số lượng: *{quantity}*. Thành tiền: *{amount}* ₫
Đối tác: {user_name} ({user_phone})
Lưu ý: _{delivery_note}_
Khách hàng thanh toán phí ship: {shipping_cost_included_text}
Người nhận: {receiver_name} ({receiver_phone})
Địa chỉ: {receiver_address}
Admin link: {url}
""".format(
        quantity=booking_data["quantity"],
        amount=intdot(booking_data["amount"]),
        user_name=user_name,
        user_phone=user_phone,
        delivery_note=delivery_note_text,
        shipping_cost_included_text=shipping_cost_included_text,
        receiver_name=booking_data["receiver_name"],
        receiver_phone=booking_data["receiver_phone"],
        receiver_address=booking_data["receiver_address"],
        url=url,
    )

    hook_telegram(telegram_text)


@shared_task(queue="post_signal")
def create_new_communication(booking_data):
    type, _ = CommunicationType.objects.get_or_create(name="App")
    response, _ = CommunicationResponse.objects.get_or_create(name="Tạo đơn")
    status, _ = CommunicationStatus.objects.get_or_create(name="Đã nhận")
    internal_comment = "Tạo đơn hàng #{} từ app".format(booking_data["id"])
    created_by = User.objects.get(id=booking_data["created_by"])

    Communication.objects.create(
        user=created_by,
        type=type,
        response=response,
        status=status,
        internal_comment=internal_comment,
        created_by=created_by,
    )


def notify_change_order_status(order):
    data = {
        "user_id": [str(order.ordered_by_id)],
        "heading": "",
        "content": "Đơn hàng của bạn (mã: {ref}) đã chuyển sang trạng thái: {status}.".format(
            ref=order.ref,
            status=order.get_status_display(),
        ),
        "data": {"uuid": order.uuid, "type": "order", "id": order.uuid},
        "type": "order",
        "notification_id": None,
    }
    send_push_notification.delay(data)


def get_image_attrs(path, name):
    full_path = os.path.join(path, name)
    file_name, file_ext = name.split('.')
    sku, no = map(lambda x: x.strip(), file_name.split('-'))
    return sku, no == '1', full_path


def import_product_image(importer):
    directory = 'media/product/importer/{}'.format(importer.id)

    # Extract
    z = zipfile.ZipFile(importer.zip_file.file, 'r')
    z.extractall(directory)
    z.close()

    # Attach to product
    products = defaultdict(list)
    for path, subdirs, files in os.walk(directory):
        for name in files:
            # Match 01234 - 1.jpg
            if not re.match(r"^\d+[ \-\d]*\.\S{3,4}$", name):
                continue

            sku, main, image = get_image_attrs(path, name)
            products[sku].append((main, image))

    for sku, attrs in products.items():
        product = Product.objects.filter(sku=sku).first()
        if not product:
            continue

        for main, image in attrs:
            img = Image(product=product, main=main, importer=importer)
            img.image.name = image[len('media/'):]
            img.save()
