# Generated by Django 2.1.7 on 2019-03-26 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0012_auto_20190324_1951'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderstatus',
            old_name='note',
            new_name='internal_comment',
        ),
    ]