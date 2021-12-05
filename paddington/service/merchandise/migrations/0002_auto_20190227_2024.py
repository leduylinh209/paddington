# Generated by Django 2.1.5 on 2019-02-27 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='shipping_method',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(help_text='kg'),
        ),
    ]