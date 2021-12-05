from rest_framework import serializers
from service.noibaiconnect.models import Quotation, Booking, BookingStatus


class BookingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookingStatus
        exclude = ()


class QuotationSerializer(serializers.ModelSerializer):

    pickup_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        input_formats=["%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M"],
    )

    class Meta:
        model = Quotation
        exclude = ('modified_by', 'modified_at')


class BookingSerializer(serializers.ModelSerializer):

    quotation = QuotationSerializer(read_only=True)
    quotation_id = serializers.IntegerField(write_only=True)
    bookingstatus_set = BookingStatusSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        exclude = ('modified_by', 'modified_at')
