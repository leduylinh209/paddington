# Generated by Django 2.1.5 on 2019-01-28 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noibaiconnect', '0002_booking_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotation',
            name='wait_time',
            field=models.FloatField(default=0),
        ),
    ]
