# Generated by Django 2.1.7 on 2019-04-17 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0020_auto_20190408_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_cost_included',
            field=models.BooleanField(default=False, verbose_name='Customer pays shipping cost'),
        ),
    ]
