# Generated by Django 2.2 on 2019-05-05 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_auto_20190502_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]