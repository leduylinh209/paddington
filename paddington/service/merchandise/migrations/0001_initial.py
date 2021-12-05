# Generated by Django 2.1.5 on 2019-02-26 15:05

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import paddington.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='product/%Y%m%d/%H%M%S/')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified at')),
                ('sku', models.CharField(max_length=128, unique=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('short_description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('long_description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('rrp', models.PositiveIntegerField(help_text='Recommended retail price in VND')),
                ('length', models.PositiveIntegerField(help_text='mm')),
                ('width', models.PositiveIntegerField(help_text='mm')),
                ('height', models.PositiveIntegerField(help_text='mm')),
                ('weight', models.PositiveIntegerField(help_text='kg')),
                ('volume', models.PositiveIntegerField(help_text='ml')),
                ('product_lifespan', models.CharField(blank=True, max_length=256, null=True)),
                ('origin', models.CharField(blank=True, max_length=128, null=True)),
                ('made_in', models.CharField(blank=True, max_length=128, null=True)),
                ('brand', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_method', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_time', models.CharField(blank=True, max_length=128, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, paddington.models.SignalSaveMixin),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified at')),
                ('code', models.CharField(max_length=64, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unit_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unit_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, paddington.models.SignalSaveMixin),
        ),
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='merchandise.Unit'),
        ),
        migrations.AddField(
            model_name='image',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='merchandise.Product'),
        ),
    ]