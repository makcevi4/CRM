# Generated by Django 4.1.7 on 2023-03-28 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_deposit_id_remove_withdraw_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='worker',
            new_name='staff',
        ),
    ]
