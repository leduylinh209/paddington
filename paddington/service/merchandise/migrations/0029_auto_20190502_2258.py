# Generated by Django 2.2 on 2019-05-02 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0028_product_packaging_specification'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='internal_comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='product',
            name='name_vn',
            field=models.CharField(db_index=True, editable=False, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='rrp',
            field=models.PositiveIntegerField(default=0, help_text='Recommended retail price in VND'),
        ),
    ]
