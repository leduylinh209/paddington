# Generated by Django 2.2 on 2019-05-02 13:05

from django.db import migrations


def make_record_from_text(apps, schema_editor):
    Product = apps.get_model("merchandise", "Product")
    Country = apps.get_model("merchandise", "Country")
    Brand = apps.get_model("merchandise", "Brand")

    for product in Product.objects.iterator():
        if product.origin_text:
            origin, _ = Country.objects.get_or_create(
                name=product.origin_text,
                code=product.origin_text,
            )
            product.origin = origin

        if product.made_in_text:
            made_in, _ = Country.objects.get_or_create(
                name=product.made_in_text,
                code=product.made_in_text,
            )
            product.made_in = made_in

        if product.brand_text:
            brand, _ = Brand.objects.get_or_create(
                name=product.brand_text,
                code=product.brand_text,
            )
            product.brand = brand

        product.save_without_signals()


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0023_auto_20190502_2010'),
    ]

    operations = [
        migrations.RunPython(make_record_from_text)
    ]
