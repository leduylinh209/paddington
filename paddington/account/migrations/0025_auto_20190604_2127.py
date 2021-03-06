# Generated by Django 2.2 on 2019-06-04 14:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0024_auto_20190517_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_cared_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_carers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_carer_added_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
