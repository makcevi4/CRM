# Generated by Django 4.1.7 on 2023-03-12 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration', models.DateTimeField(auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/clients/%Y/%m')),
                ('birthday', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('completed', 'Completed'), ('conversion', 'Conversion'), ('retention', 'Retention'), ('rejected', 'Rejected')], default=('conversion', 'Conversion'), max_length=25)),
                ('project', models.CharField(choices=[('inv', 'Investing'), ('cl', 'Cloud solutions'), ('dr', 'Drainer'), ('ex', 'Exchanger')], max_length=100)),
                ('contact_telegram', models.CharField(blank=True, max_length=50, null=True)),
                ('contact_whatsapp', models.CharField(blank=True, max_length=50, null=True)),
                ('contact_discord', models.CharField(blank=True, max_length=50, null=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('contact_phone', models.BigIntegerField(blank=True, null=True)),
                ('location_city', models.CharField(max_length=100)),
                ('location_country', models.CharField(max_length=100)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Клиенты',
                'ordering': ['-registration'],
            },
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration', models.DateTimeField(auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Управляющие',
            },
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration', models.DateTimeField(auto_created=True)),
                ('telegram', models.CharField(blank=True, max_length=25, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.manager')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Клиенты',
            },
        ),
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('date', models.DateTimeField(auto_created=True)),
                ('uid', models.UUIDField(default=uuid.UUID('3cc2d1be-5e7e-46ad-a8eb-4f20849ed51b'), editable=False, primary_key=True, serialize=False)),
                ('sum', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
            ],
            options={
                'verbose_name_plural': 'Выводы',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('date', models.DateTimeField(auto_created=True)),
                ('uid', models.UUIDField(default=uuid.UUID('bc891e05-007c-465b-b2b1-9746d6fdb877'), editable=False, primary_key=True, serialize=False)),
                ('sum', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
            ],
            options={
                'verbose_name_plural': 'Депозиты',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('date', models.DateTimeField(auto_created=True)),
                ('uid', models.UUIDField(default=uuid.UUID('d7e4bd4d-156e-406a-8d75-6cd45eea0b08'), editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('worker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='client',
            name='worker_conversion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='conversion', to='api.worker'),
        ),
        migrations.AddField(
            model_name='client',
            name='worker_retention',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='retention', to='api.worker'),
        ),
    ]
