# Generated by Django 2.2 on 2019-05-02 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0021_order_shipping_cost_included'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='brand',
            new_name='brand_text',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='made_in',
            new_name='made_in_text',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='origin',
            new_name='origin_text',
        ),
    ]