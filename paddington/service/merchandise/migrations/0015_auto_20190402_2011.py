# Generated by Django 2.1.7 on 2019-04-02 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0014_product_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='shipping_time',
            field=models.TextField(blank=True, null=True),
        ),
    ]
