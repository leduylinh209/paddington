# Generated by Django 2.2 on 2019-05-29 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0032_auto_20190507_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', '1. Chờ xác nhận'), ('confirmed', '2. Đã xác nhận'), ('ready_to_ship', '3. Sẵn sàng giao hàng'), ('dispatched', '4. Đã giao hàng cho shipper'), ('shipping', '5. Shipper đang giao hàng'), ('delivered', '6. Đã giao hàng cho người nhận'), ('completed', '7. Đã hoàn thành và thanh toán'), ('cancelled', '8. Đã huỷ'), ('problem', '9. Gặp vấn đề'), ('consigned', '10. Đã ký gửi')], db_index=True, default='new', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.CharField(choices=[('new', '1. Chờ xác nhận'), ('confirmed', '2. Đã xác nhận'), ('ready_to_ship', '3. Sẵn sàng giao hàng'), ('dispatched', '4. Đã giao hàng cho shipper'), ('shipping', '5. Shipper đang giao hàng'), ('delivered', '6. Đã giao hàng cho người nhận'), ('completed', '7. Đã hoàn thành và thanh toán'), ('cancelled', '8. Đã huỷ'), ('problem', '9. Gặp vấn đề'), ('consigned', '10. Đã ký gửi')], default='new', max_length=64),
        ),
    ]
