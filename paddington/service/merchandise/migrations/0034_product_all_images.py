# Generated by Django 2.2 on 2019-06-02 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0033_auto_20190529_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='all_images',
            field=models.TextField(editable=False, null=True),
        ),
    ]
