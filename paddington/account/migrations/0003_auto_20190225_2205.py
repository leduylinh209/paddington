# Generated by Django 2.1.5 on 2019-02-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20190225_2134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='interest',
            field=models.TextField(blank=True, null=True),
        ),
    ]
