from django.db import models
from paddington.models import TrackingAbstractModel
from service.noibaiconnect.constants import STATUS_CHOICE


class Quotation(TrackingAbstractModel):
    """
    Model for a quotation

    - `start_point` (required|min:3): điểm xuất phát
    - `end_point` (required|min:3): điểm cuối, nếu điểm cuối là Nội Bài, để giá trị là noi bai, ha noi, viet nam
    - `stop_points` (nullable|string): danh sách điểm dừng giữa đường (nếu có), cách nhau bởi dấu **;**

    - `trip_distance` (default 0, type: meter): tổng độ dài chuyến đi (chiều đi), bao gồm các điểm dừng
    - `trip_duration`(default 0, type: second): thời gian di chuyển chuyến đi (chiều đi), bao gồm các điểm dừng
    - `trip_type` (default 0, type: number): 0 nếu là chuyến tiễn (đến sân bay), 1 nếu là chuyến đón (từ sân bay đi)

    - `num_stop_points` (default 0, type: number): số điểm dừng
    - `num_seats` (default 4, type: number): số chỗ
    - `wait_time` (default 0, type: hour): tổng số giờ xe phải đợi

    - `is_round_trip` (default false): chuyến đi hai chiều
    - `is_long_distance_trip` (default false): chuyến đi đường dài

    - `return_trip_distance` (default 0, type: meter): tổng độ dài chuyến về, bao gồm các điểm dừng
    - `pickup_datetime` (default empty string, format: 'YYYY-mm-dd HH:ii:ss): thời gian đón
    """
    # Start input fields
    start_point = models.CharField(max_length=1024)
    end_point = models.TextField(max_length=1024)
    stop_points = models.TextField(blank=True, null=True)
    num_stop_points = models.IntegerField(default=0)

    trip_distance = models.IntegerField()
    trip_duration = models.IntegerField()
    trip_type = models.IntegerField(default=0)

    num_seats = models.IntegerField(default=4)
    wait_time = models.FloatField(default=0)

    is_round_trip = models.BooleanField(default=False)
    is_long_distance_trip = models.BooleanField(default=False)

    return_trip_distance = models.IntegerField(default=0)
    pickup_datetime = models.DateTimeField()
    # End input fields

    # Start output (Quotation)
    total_fee = models.IntegerField(default=0)
    commission = models.IntegerField(default=0)
    night_fee = models.IntegerField(default=0)
    stop_fee = models.IntegerField(default=0)
    wait_fee = models.IntegerField(default=0)
    # End output (Quotation)


class Booking(TrackingAbstractModel):
    """
    Model for a booking
    """
    # Start input
    customer_name = models.CharField(max_length=256)
    customer_phone = models.CharField(max_length=256)

    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, editable=False)
    # End input

    # Start output (Booking), to compare Quotation & Booking
    total_fee = models.IntegerField(default=0)
    commission = models.IntegerField(default=0)
    night_fee = models.IntegerField(default=0)
    stop_fee = models.IntegerField(default=0)
    wait_fee = models.IntegerField(default=0)
    order_id = models.CharField(verbose_name="Supplier ref. no.", null=True,
                                max_length=256, editable=False)
    # End output (Booking)

    status = models.CharField(choices=STATUS_CHOICE, max_length=32, editable=False,
                              default=STATUS_CHOICE[0][0])
    note = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        unique_together = (('created_by', 'quotation'),)


class BookingStatus(models.Model):
    """
    Model for saving booking status history
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,
                                editable=False)

    status = models.CharField(choices=STATUS_CHOICE, max_length=32, editable=False,
                              default=STATUS_CHOICE[0][0], db_index=True)
    driver_name = models.CharField(max_length=256, editable=False, null=True)
    driver_number = models.CharField(max_length=32, editable=False, null=True)
    plate = models.CharField(max_length=32, editable=False, null=True)

    cancel_reason = models.TextField(editable=False, null=True)

    created_at = models.DateTimeField(
        "Created at",
        blank=True,
        null=True,
        auto_now_add=True,
        db_index=True,
        editable=False,
    )

    def __str__(self):
        return "{} #{}".format(self.__class__.__name__, self.id)

    class Meta:
        unique_together = (('booking', 'status'),)
        verbose_name = "Booking status"
        verbose_name_plural = "Booking status"
