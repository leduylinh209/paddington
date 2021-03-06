# Generated by Django 2.2 on 2019-05-02 13:45

from django.db import migrations


def init_internal_state(apps, schema_editor):
    Product = apps.get_model("merchandise", "Product")
    InternalState = apps.get_model("merchandise", "InternalState")

    for code, name in (
        ("raw", "1. Sơ khai"),
        ("missing_images", "2. Thiếu ảnh"),
        ("missing_content", "3. Thiếu nội dung"),
        ("spellcheck", "4. Cần kiểm tra chính tả và tiếng Việt"),
        ("formatting", "5. Cần trình bày đẹp"),
        ("final_check", "6. Cần kiểm tra lần cuối"),
        ("ready", "7. Sẵn sàng"),
    ):
        InternalState.objects.get_or_create(
            code=code,
            name=name,
        )

    final_check = InternalState.objects.get(code="final_check")
    for product in Product.objects.iterator():
        product.internal_state = final_check
        product.save_without_signals()


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0026_auto_20190502_2045'),
    ]

    operations = [
        migrations.RunPython(init_internal_state)
    ]
