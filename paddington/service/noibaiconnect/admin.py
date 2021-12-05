from django.contrib import admin

from paddington.admin import TrackingAdminMixin
from service.noibaiconnect.models import Booking, Quotation, BookingStatus
from service.utils import format_date_time_zone


@admin.register(Quotation)
class QuotationAdmin(TrackingAdminMixin, admin.ModelAdmin):
    readonly_fields = ['created_by', 'created_at', 'modified_by', 'modified_at']


class BookingStatusInlineAdmin(admin.TabularInline):
    model = BookingStatus
    fields = readonly_fields = [
        'status', 'driver_name', 'driver_number', 'plate', 'cancel_reason',
    ]
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(Booking)
class BookingAdmin(TrackingAdminMixin, admin.ModelAdmin):
    list_display = [
        '__str__', 'customer_name', 'customer_phone',
        'start_point', 'end_point', 'pickup_datetime', 'created_by', 'created_at',
        'status', 'quotation',
    ]
    readonly_fields = [
        'created_by', 'created_at', 'modified_by', 'modified_at', 'order_id',
        'start_point', 'end_point', 'stop_points', 'num_stop_points',
        'trip_distance', 'trip_duration', 'trip_type', 'num_seats',
        'wait_time', 'is_round_trip', 'is_long_distance_trip',
        'return_trip_distance', 'pickup_datetime',
        'total_fee_', 'commission_',
        'night_fee_', 'stop_fee_', 'wait_fee_',
        'status',
    ]
    inlines = [BookingStatusInlineAdmin]

    fieldsets = (
        ('Booking', {
            'fields': (
                'status',
                ('customer_name', 'customer_phone'),
                ('start_point', 'end_point'),
                'pickup_datetime',
                ('stop_points', 'num_stop_points'),
                ('trip_distance', 'trip_duration'),
                'trip_type', 'num_seats',
                'wait_time', 'is_round_trip', 'is_long_distance_trip',
                'return_trip_distance',
                ('created_by', 'created_at'),
                'order_id', 'note',
            ),
        }),
        ('Fee & Commission', {
            'fields': (
                ('total_fee', 'commission'),
                ('night_fee', 'stop_fee', 'wait_fee'),
            )
        }),
        ('Quotation', {
            'fields': (
                ('total_fee_', 'commission_'),
                ('night_fee_', 'stop_fee_', 'wait_fee_'),
            )
        }),
        ('Status', {
            'classes': ('placeholder bookingstatus_set-group',),
            'fields': (),
        }),
        ('System', {
            'fields': (
                ('modified_by', 'modified_at'),
            ),
        }),
    )

    def start_point(self, obj):
        return obj.quotation.start_point

    def end_point(self, obj):
        return obj.quotation.end_point

    def stop_points(self, obj):
        return obj.quotation.stop_points

    def num_stop_points(self, obj):
        return obj.quotation.num_stop_points

    def trip_distance(self, obj):
        return obj.quotation.trip_distance

    def trip_duration(self, obj):
        return obj.quotation.trip_duration

    def trip_type(self, obj):
        return obj.quotation.trip_type

    def num_seats(self, obj):
        return obj.quotation.num_seats

    def wait_time(self, obj):
        return obj.quotation.wait_time

    def is_round_trip(self, obj):
        return obj.quotation.is_round_trip

    def is_long_distance_trip(self, obj):
        return obj.quotation.is_long_distance_trip

    def return_trip_distance(self, obj):
        return obj.quotation.return_trip_distance

    def pickup_datetime(self, obj):
        return format_date_time_zone(obj.quotation.pickup_datetime)

    def total_fee_(self, obj):
        return obj.quotation.total_fee

    def commission_(self, obj):
        return obj.quotation.commission

    def night_fee_(self, obj):
        return obj.quotation.night_fee

    def stop_fee_(self, obj):
        return obj.quotation.stop_fee

    def wait_fee_(self, obj):
        return obj.quotation.wait_fee
