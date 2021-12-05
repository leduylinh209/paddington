# Define views here
from account.models import Notification, Transaction
from account.serializers import (
    MyFriendSerializer,
    MyRegisterSerializer,
    NotificationSerializer,
    TransactionSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer
)
from account.tasks import slack_hook_new_signup
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth.app_settings import TokenSerializer, create_token
from rest_auth.models import TokenModel
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)

logger = logging.getLogger("Account")

# authy_api = AuthyApiClient("9s0JxAe9oPc4DHAN2dfZzCQHhiEqrDr7")


class RegisterView(CreateAPIView):
    serializer_class = MyRegisterSerializer
    permission_classes = [AllowAny]
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        print("create user")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_response_data(user),
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        create_token(self.token_model, user, serializer)
        slack_hook_new_signup.delay(user.id)
        return user


class FriendView(ListAPIView):
    """
    API for booking a trip
    """

    queryset = User.objects.all()
    serializer_class = MyFriendSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(profile__referred_by=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Attach referred_by info
        profile = getattr(self.request.user, "profile", None)
        referred_by = profile and profile.referred_by
        if referred_by:
            response.data["referred_by"] = MyFriendSerializer(instance=referred_by).data

        return response


class TransactionView(ListAPIView):
    """
    API for listing transactions
    """

    queryset = Transaction.objects.filter(success=True)
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).order_by("-id")


class NotificationListView(ListAPIView):
    """
    API for listing transactions
    """

    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.user_notifications(user=self.request.user).order_by("-id")


class NotificationDetailView(RetrieveAPIView):
    """
    API for listing transactions
    """

    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.user_notifications(user=self.request.user).order_by("-id")


class SendOTPView(CreateAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print("create user")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        print("create done")
        headers = self.get_success_headers(serializer.data)
        print("get header done")
        return Response(
            res, status=status.HTTP_200_OK, headers=headers,
        )

    def perform_create(self, serializer):
        return serializer.save()

class VerifyOTPView(CreateAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            res, status=status.HTTP_200_OK, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()


register_view = RegisterView.as_view()
friend_view = FriendView.as_view()
transaction_view = TransactionView.as_view()
notification_list_view = NotificationListView.as_view()
notification_detail_view = NotificationDetailView.as_view()
send_otp_view = SendOTPView.as_view()
verify_otp_view = VerifyOTPView.as_view()
