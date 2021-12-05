from django.db import IntegrityError
import traceback
from django.shortcuts import get_object_or_404
from rest_framework import permissions, views, generics, pagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from service.noibaiconnect.api_caller import NoiBaiConnectAPI
from service.noibaiconnect.models import Quotation, Booking
from service.noibaiconnect.tasks import slack_hook_new_order
from service.noibaiconnect.serializers import (BookingSerializer,
                                               QuotationSerializer)

booking_properties = [
    'total_fee', 'commission', 'night_fee', 'stop_fee', 'wait_fee', 'order_id'
]


class QuotationAPI(views.APIView):
    """
    API for getting quotation of a trip
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        quotation_serializer = QuotationSerializer(data=request.data)
        quotation_serializer.is_valid(raise_exception=True)

        resp, status = NoiBaiConnectAPI().get_price(quotation_serializer.validated_data)
        quotation = None
        if status == 200:
            # Save quotation to our system
            extra_properties = {
                k: resp[k]
                for k in booking_properties
                if k in resp
            }
            quotation = quotation_serializer.save(
                created_by=request.user,
                **extra_properties
            )

        if quotation is not None:
            return Response(QuotationSerializer(quotation).data, status=status)
        return Response(resp, status=status)


class BookingAPI(generics.ListCreateAPIView):
    """
    API for booking a trip
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        booking_serializer = BookingSerializer(data=request.data)
        booking_serializer.is_valid(raise_exception=True)

        validated_data = booking_serializer.validated_data.copy()
        quotation = get_object_or_404(Quotation, pk=validated_data['quotation_id'])
        validated_data.update(**QuotationSerializer(quotation).data)

        resp, status = NoiBaiConnectAPI().book_a_trip(validated_data)
        booking = None

        if status == 200:
            # Save booking to our system
            extra_properties = {
                k: resp[k]
                for k in booking_properties
                if k in resp
            }

            try:
                booking = booking_serializer.save(
                    created_by=request.user,
                    **extra_properties
                )
                resp = BookingSerializer(booking).data
                slack_hook_new_order.delay(resp)
            except IntegrityError:
                pass
            except Exception as e:
                traceback.print_exc()
                return Response({"detail": str(e)}, status=500)

        if booking is not None:
            return Response(resp, status=status)
        return Response(resp, status=status)


quotation = QuotationAPI.as_view()
booking = BookingAPI.as_view()
