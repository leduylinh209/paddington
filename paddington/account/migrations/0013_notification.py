# Generated by Django 2.1.7 on 2019-04-21 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0012_transaction_post_transaction_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Created at')),
                ('title', models.CharField(blank=True, max_length=36, null=True)),
                ('content', models.TextField(max_length=148)),
                ('type', models.CharField(choices=[('personal', 'personal'), ('promotion', 'promotion'), ('product', 'product'), ('order', 'order'), ('training', 'training'), ('friend', 'friend'), ('balance', 'balance'), ('other', 'other')], default='personal', max_length=64)),
                ('success', models.BooleanField(default=True, editable=False)),
                ('one_signal_id', models.CharField(editable=False, max_length=64, null=True)),
                ('one_signal_count', models.IntegerField(default=0, editable=False)),
                ('remaining', models.IntegerField(default=0, editable=False)),
                ('failed', models.IntegerField(default=0, editable=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notification_created', to=settings.AUTH_USER_MODEL)),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
