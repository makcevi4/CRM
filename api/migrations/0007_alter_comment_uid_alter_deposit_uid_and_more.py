# Generated by Django 4.1.7 on 2023-03-13 15:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_worker_type_alter_comment_uid_alter_deposit_uid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('98bcaf05-a45d-4c17-a49b-cea3d4646fef'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('92d5c3fe-bd0e-4def-a787-18944cbc2351'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('11240168-4d6e-4df6-b5f5-c38fd16ec535'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='worker',
            name='type',
            field=models.CharField(choices=[('conversion', 'Конверсия'), ('retention', 'Ретен')], max_length=25),
        ),
    ]