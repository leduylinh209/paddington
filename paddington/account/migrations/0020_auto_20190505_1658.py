# Generated by Django 2.2 on 2019-05-05 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_notification_read'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'permissions': (('can_update_referred_by', 'Can change referred_by'),)},
        ),
    ]
