from django.db.models.signals import post_save
from django.utils import timezone

from account.models import Notification, Profile, Transaction, Wallet
from account.tasks import notify_change_balance, notify_manually


def profile_post_save_signal_handler(sender, instance, created, **kwargs):
    if getattr(instance, '_disable_signals', False):
        return

    if sender == Profile:
        user = instance.user

        if user and not hasattr(user, 'wallet'):
            Wallet.objects.create(user=user)

        if instance.cared_by != instance.last_cared_by:
            instance.last_cared_by = instance.cared_by
            instance.last_carer_added_at = timezone.now()

            instance.save_without_signals()

    elif sender == Transaction:

        if instance.success:
            notify_change_balance(instance)

    elif sender == Notification:

        if created:
            notify_manually.apply_async(args=[instance.id], countdown=5)


def register_signals():
    post_save.connect(profile_post_save_signal_handler)
