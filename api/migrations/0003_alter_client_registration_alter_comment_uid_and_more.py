# Generated by Django 4.1.7 on 2023-03-13 13:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_client_options_alter_comment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='registration',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('6763cb93-90a9-4bf9-b6f4-df179d62fa5c'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('f4e20b13-2121-48dc-8023-94bd98c01614'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('5a368664-3d01-4b24-ad4a-3fb467a1bc47'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
