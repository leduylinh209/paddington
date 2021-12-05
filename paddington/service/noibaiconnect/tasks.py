from celery import shared_task, task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.models import User

from service.noibaiconnect.api_caller import NoiBaiConnectAPI
from service.utils import hook_slack, intdot

logger = get_task_logger(__name__)


@shared_task(queue="slack_hook")
def slack_hook_new_order(booking_data):
    url = "http://{}/admin/noibaiconnect/booking/{}/change/".format(
        settings.BASE_HOST,
        booking_data["id"],
    )
    created_by = User.objects.get(id=booking_data["created_by"])
    profile = hasattr(created_by, 'profile') and created_by.profile

    user_name = (created_by.last_name + created_by.first_name) or created_by.username
    user_phone = profile and profile.phone

    fallback = "Đơn hàng mới vừa được tạo: <{url}|#{id}>".format(
        url=url,
        id=booking_data["id"],
    )

    text = """
Đối tác: {user_name} (<tel:{user_phone}|{user_phone}>)
Sản phẩm: Noibai Connect
Khách: {customer_name} (<tel:{customer_phone}|{customer_phone}>)
Mô tả: Đi từ {start_point} đến {end_point}
Phí: *{total_fee}* ₫, hoa hồng: *{commission}* ₫
    """.format(
        user_name=user_name,
        user_phone=user_phone,
        customer_name=booking_data["customer_name"],
        customer_phone=booking_data["customer_phone"],
        total_fee=intdot(booking_data["total_fee"]),
        commission=intdot(booking_data["commission"]),
        start_point=booking_data["quotation"]["start_point"],
        end_point=booking_data["quotation"]["end_point"],
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


@task()
def check_booking_status():
    from service.noibaiconnect.models import Booking
    for order_id in Booking.objects.filter(
        status__in=["pending", "confirmed"]
    ).values_list("order_id", flat=True):
        check_booking_status_for_order(order_id)


@shared_task(queue="status_check")
def check_booking_status_for_order(order_id):
    from service.noibaiconnect.models import Booking, BookingStatus

    data, status = NoiBaiConnectAPI().check_booking_status([order_id])

    logger.debug('Check booking status: %s %s', status, data)
    if status != 200:
        return

    booking = Booking.objects.get(order_id=order_id)
    latest_status = data[0]["order_status"]["name"]

    if booking.status == latest_status:
        return

    BookingStatus.objects.update_or_create(
        booking=booking,
        status=latest_status,
        defaults=data[0]["order_status"]["detail"],
    )
    booking.status = latest_status
    booking.save()
