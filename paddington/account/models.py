import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from model_utils.models import TimeStampedModel

from paddington.constants import (BANK_CHOICES, EXPERIENCE_CHOICES,
                                  NOTIFICATION_TYPES, SEX_CHOICES)
from paddington.models import (CreatedAbstractModel, ModifiedAbstractModel,
                               SignalSaveMixin)


class Profile(SignalSaveMixin, TimeStampedModel):
    """
    Profile extends Django User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=32, unique=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    id_card_no = models.CharField(max_length=32, null=True, blank=True)
    sex = models.CharField(max_length=32, choices=SEX_CHOICES, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    bank_cod = models.CharField(max_length=16, choices=BANK_CHOICES,
                                null=True, blank=True)
    bank_account_no = models.CharField(max_length=32, null=True, blank=True)
    bank_account_name = models.CharField(max_length=64, null=True, blank=True)
    personal_facebook = models.CharField(max_length=256, null=True, blank=True)
    business_facebook = models.CharField(max_length=256, null=True, blank=True)

    online_sales_experience = models.CharField(max_length=32, choices=EXPERIENCE_CHOICES,
                                               null=True, blank=True)

    interest = models.TextField(null=True, blank=True, verbose_name="Interests")
    internal_comment = models.TextField(null=True, blank=True)

    shopee_shop = models.CharField(max_length=256, null=True, blank=True)
    lazada_shop = models.CharField(max_length=256, null=True, blank=True)
    tiki_shop = models.CharField(max_length=256, null=True, blank=True)

    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='referrals')

    cared_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='carers')

    last_cared_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      null=True, editable=False,
                                      related_name='last_carers')
    last_carer_added_at = models.DateTimeField(null=True, editable=False)

    can_refer = models.BooleanField(default=True)

    last_interaction_at = models.DateTimeField(null=True, editable=False)
    last_order_at = models.DateTimeField(null=True, editable=False)

    last_notification = models.ForeignKey('account.Notification', null=True,
                                          editable=False, on_delete=models.SET_NULL)

    @property
    def notification_count(self):
        if self.last_notification_id:
            return Notification.user_notifications(
                user=self.user,
            ).filter(
                id__gt=self.last_notification_id,
            ).count()
        return Notification.user_notifications(user=self.user).count()

    @property
    def full_name(self):
        return (self.user.last_name + " " + self.user.first_name) or self.user.username

    def __str__(self):
        return "Profile {}".format(self.phone)

    def clean(self):
        if self.phone:
            self.phone = re.sub('[^0-9]', '', self.phone)

    class Meta:
        permissions = (
            ("can_update_referred_by", "Can change referred_by"),
            ("can_update_cared_by", "Can change cared_by"),
        )


class Wallet(ModifiedAbstractModel):
    """
    This is the user's wallet
    """
    user = models.OneToOneField(User, editable=False,
                                on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0, editable=False)

    def check_amount_valid(self, amount):
        """
        Only check for non-negative balance for now
        """
        if not amount or type(amount) is not int:
            return False, "Invalid amount"

        if self.balance + amount < 0:
            return False, "Insufficient balance"

        return True, None

    def __str__(self):
        return "Wallet of user {}".format(self.user)


class Transaction(CreatedAbstractModel):
    """
    This save all user's transactions that will change wallet's balance
    """
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE,
                               editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.BigIntegerField(
        help_text="Positive number for recharging, negative number for withdrawing"
    )
    post_transaction_balance = models.PositiveIntegerField(default=0, editable=False)

    description = models.CharField(max_length=512)

    success = models.BooleanField(editable=False)
    note = models.TextField(editable=False, null=True)

    def clean(self):
        if not hasattr(self, 'user'):
            return

        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        valid, reason = wallet.check_amount_valid(self.amount)

        if not valid:
            raise ValidationError(reason)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Not able to change old transaction
        if self.id:
            return

        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        self.wallet = wallet

        self.success, self.note = wallet.check_amount_valid(self.amount)

        if self.success:
            wallet.balance += self.amount
            wallet.modified_by = self.user
            wallet.save()

        self.post_transaction_balance = wallet.balance

        super().save(*args, **kwargs)

    def __str__(self):
        return "Transaction #{}".format(self.id)


class Notification(SignalSaveMixin, CreatedAbstractModel):
    """
    Model for saving user notification
    """
    title = models.CharField(max_length=36, null=True, blank=True)
    content = models.TextField(max_length=148)

    url = models.URLField(null=True, blank=True)

    all_users = models.BooleanField(default=False)
    recipients = models.ManyToManyField(User, blank=True)

    type = models.CharField(
        max_length=64,
        choices=NOTIFICATION_TYPES,
        default=NOTIFICATION_TYPES[0][0],
    )

    object_id = models.CharField(
        null=True, blank=True, max_length=128,
        help_text="ID of referred object",
    )

    success = models.BooleanField(default=True, editable=False)

    one_signal_id = models.CharField(max_length=64, null=True, editable=False)
    one_signal_count = models.IntegerField(default=-1, editable=False)

    remaining = models.IntegerField(default=-1, editable=False)
    failed = models.IntegerField(default=-1, editable=False)

    @classmethod
    def user_notifications(cls, user):
        return cls.objects.filter(Q(recipients=user) | Q(all_users=True)).distinct()

    def __str__(self):
        return "Notification #{}".format(self.id)


class CommunicationType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CommunicationStatus(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Communication status"
        verbose_name_plural = "Communication statuses"


class CommunicationResponse(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Communication(SignalSaveMixin, CreatedAbstractModel):
    """
    Model for communicating with customers
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    type = models.ForeignKey(CommunicationType, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(CommunicationStatus, null=True, on_delete=models.SET_NULL)
    response = models.ForeignKey(CommunicationResponse, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    internal_comment = models.TextField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    manual_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Communication #{}".format(self.id)

class Store(SignalSaveMixin, TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following', related_query_name='following', blank=True)


def get_user_str(self):
    return "{} ({} {})".format(self.username, self.last_name, self.first_name)


User.add_to_class("__str__", get_user_str)
