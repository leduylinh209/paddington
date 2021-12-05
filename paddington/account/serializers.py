from django.contrib.auth.models import User
from django.utils import timezone
from rest_auth.serializers import LoginSerializer
from rest_framework import exceptions, serializers

from account.models import Notification, Profile, Transaction, Wallet
from paddington.constants import BANK_CHOICES, EXPERIENCE_CHOICES, SEX_CHOICES
from service.utils import standardize_phone_number

from authy.api import AuthyApiClient

import logging

authy_api = AuthyApiClient("9s0JxAe9oPc4DHAN2dfZzCQHhiEqrDr7")


class MyLoginSerializer(LoginSerializer):
    """
    Custom validate for our case
    """

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        profile = None
        user = None

        if username:
            try:
                profile = Profile.objects.get(phone=username)
            except Profile.DoesNotExist:
                pass

        if profile:
            user = self._validate_username_email(profile.user.username, "", password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = "User account is disabled."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Unable to log in with provided credentials."
            raise exceptions.ValidationError(msg)

        attrs["user"] = user
        return attrs


logger = logging.getLogger(__name__)


class MyRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16, min_length=10, required=True)
    name = serializers.CharField(max_length=60, required=True)
    referred_by = serializers.CharField(max_length=16, required=False)

    address = serializers.CharField(max_length=512, required=False)
    personal_facebook = serializers.CharField(max_length=512, required=False)

    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_name(self, name):
        return name.strip().title()

    def validate_referred_by(self, phone):
        return phone.replace(".", "")

    def validate_phone(self, phone):
        print("check phone")
        phone = standardize_phone_number(phone)
        if phone is None:
            raise serializers.ValidationError("Số điện thoại không hợp lệ")
        return phone

    def validate(self, data):
        print("validate")
        # Check password match
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("The two password fields didn't match.")

        # Check referred_by
        # if not Profile.objects.filter(
        #     phone=data["referred_by"], can_refer=True
        # ).exists():
        #     raise serializers.ValidationError(
        #         "Mã giới thiệu chưa đúng. Xin vui lòng thử lại."
        #     )

        # Check phone
        if Profile.objects.filter(phone=data["phone"]).exists():
            raise serializers.ValidationError(
                "Số điện thoại đã tồn tại. Xin vui lòng thử lại."
            )

        return data

    def save(self, request):
        print("save")
        # referred_by_profile = Profile.objects.get(
        #     phone=self.validated_data["referred_by"]
        # )
        # If name has 1 word, it's first_name, else, first word is last_name
        name = self.validated_data["name"].split()
        last_name = ""
        first_name = name[0]
        if len(name) > 1:
            first_name = " ".join(name[1:])
            last_name = name[0]

        user, created = User.objects.get_or_create(
            username=self.validated_data["phone"],
            defaults={"first_name": first_name, "last_name": last_name,},
        )

        # Reset password when user has no profile or newly created
        if created or not hasattr(user, "profile"):
            user.set_password(self.validated_data["password1"])
            user.last_login = timezone.now()
            user.save()

            Profile.objects.create(
                # referred_by=referred_by_profile.user,
                user=user,
                phone=self.validated_data["phone"],
                address=self.validated_data.get("address"),
                personal_facebook=self.validated_data.get("personal_facebook"),
            )

            return user

        raise serializers.ValidationError("Số điện thoại đã tồn tại!")


class SendOTPSerializer(serializers.Serializer):
    country_code = serializers.CharField(max_length=3, min_length=2, required=True)
    phone = serializers.CharField(max_length=16, required=True)
    verify_by = serializers.CharField()

    def validate(self, data):
        logger.info(data.get("phone"))
        # Check phone
        if Profile.objects.filter(phone="0"+data["phone"]).exists():
            raise serializers.ValidationError(
                "Số điện thoại đã tồn tại. Xin vui lòng thử lại."
            )

        return data

    # def save(self):
    #     logger.debug(self.validated_data)
    #     return self.validated_data

    def save(self):
        res = authy_api.phones.verification_start(
            self.validated_data["phone"],
            self.validated_data["country_code"],
            via=self.validated_data["verify_by"],
        )
        if res.ok():
            return res.content
        
        raise serializers.ValidationError("Can't verify phone number")

class VerifyOTPSerializer(serializers.Serializer):
    country_code = serializers.CharField(max_length=3, min_length=2, required=True)
    phone = serializers.CharField(max_length=16, required=True)
    verify_code = serializers.CharField()

    def save(self):
        res = authy_api.phones.verification_check(
            self.validated_data["phone"],
            self.validated_data["country_code"],
            self.validated_data["verify_code"]
        )
        
        if res.ok():
            return res.content

        raise serializers.ValidationError("Wrong verify code")


PROFILE_UPDATE_FIELDS = (
    "email",
    "address",
    "id_card_no",
    "sex",
    "date_of_birth",
    "bank_cod",
    "bank_account_no",
    "bank_account_name",
    "personal_facebook",
    "business_facebook",
    "online_sales_experience",
    "interest",
    "shopee_shop",
    "lazada_shop",
    "tiki_shop",
    "last_notification_id",
)


class ProfileSerializer(serializers.ModelSerializer):

    date_of_birth = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["%d-%m-%Y", "%Y-%m-%d"],
        required=False,
        allow_null=True,
    )

    notification_count = serializers.ReadOnlyField()
    last_notification_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = PROFILE_UPDATE_FIELDS + ("notification_count",)


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance"]


class MyFriendSerializer(serializers.ModelSerializer):

    completed_order_count = serializers.SerializerMethodField()

    def get_completed_order_count(self, obj):
        return obj.order_set.filter(status="completed").count()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "date_joined",
            "completed_order_count",
        )


class MyUserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    profile = ProfileSerializer()
    id = serializers.ReadOnlyField()

    choices = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        if not hasattr(instance, "profile"):
            return instance

        # Update profile
        profile_data = validated_data.pop("profile")
        profile = instance.profile
        for attr in PROFILE_UPDATE_FIELDS:
            if attr in profile_data:
                setattr(profile, attr, profile_data[attr])
        profile.save()

        return instance

    def get_phone(self, user):
        return getattr(user, "profile", None) and user.profile.phone

    def get_choices(self, user):
        return {
            "sex": SEX_CHOICES,
            "experience": EXPERIENCE_CHOICES,
            "bank": BANK_CHOICES,
        }

    def get_wallet(self, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        return WalletSerializer(instance=wallet).data

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "profile",
            "choices",
            "wallet",
            "id",
            "phone",
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("amount", "post_transaction_balance", "description", "created_at")


class NotificationSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()
    content = serializers.ReadOnlyField()
    type = serializers.ReadOnlyField()
    object_id = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Notification
        fields = ("id", "title", "content", "type", "object_id", "created_at", "url")

