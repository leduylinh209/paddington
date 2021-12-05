# Generated by Django 2.1.7 on 2019-03-25 14:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0006_auto_20190309_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='can_refer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to=settings.AUTH_USER_MODEL),
        ),
    ]