# Generated by Django 2.1.5 on 2019-03-06 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0004_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='height',
            field=models.PositiveIntegerField(blank=True, help_text='mm', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='length',
            field=models.PositiveIntegerField(blank=True, help_text='mm', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='volume',
            field=models.PositiveIntegerField(blank=True, help_text='ml', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, help_text='kg', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='width',
            field=models.PositiveIntegerField(blank=True, help_text='mm', null=True),
        ),
    ]
