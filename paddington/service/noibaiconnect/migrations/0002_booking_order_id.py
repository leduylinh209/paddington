# Generated by Django 2.1.5 on 2019-01-24 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noibaiconnect', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='order_id',
            field=models.IntegerField(default=0, editable=False, verbose_name='Supplier ref. no.'),
        ),
    ]
