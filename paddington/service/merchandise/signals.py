from django.db.models.signals import post_save
from django.utils import timezone
from unidecode import unidecode

from service.merchandise.models import (Order, OrderStatus, Product,
                                        ProductImageImporter)
from service.merchandise.tasks import (import_product_image,
                                       notify_change_order_status)


def order_post_save_signal_handler(sender, instance, created, **kwargs):
    if getattr(instance, '_disable_signals', False):
        return

    if sender == Order:
        # Update status for order
        order_status = instance.orderstatus_set.last()
        if not order_status:
            order_status, _ = OrderStatus.objects.get_or_create(order=instance)

        if instance.status != order_status.status:
            instance.status = order_status.status
            instance.save_without_signals()
            notify_change_order_status(instance)

        if hasattr(instance.ordered_by, 'profile'):
            instance.ordered_by.profile.last_order_at = timezone.now()
            instance.ordered_by.profile.save_without_signals()

    elif sender == OrderStatus:
        # FIXME: Update created_by for OrderStatus based on Order, this is not thread-safe
        # but for the time being, should be acceptable
        if not instance.created_by:
            instance.created_by = instance.order.modified_by
        instance.modified_by = instance.order.modified_by
        instance.save_without_signals()

        order_post_save_signal_handler(Order, instance.order, created, **kwargs)

    elif sender == Product:
        # Cache categories for searching
        instance.categories = '|'.join([
            c.category.name
            for c in instance.productcategory_set.all()
        ])
        instance.categories_vn = unidecode(instance.categories)
        instance.name_vn = unidecode(instance.name)

        # Cache images for serving
        instance.all_images = instance.get_all_images()

        instance.save_without_signals()

    elif sender == ProductImageImporter:

        if created:
            import_product_image(instance)


def register_signals():
    post_save.connect(order_post_save_signal_handler)
