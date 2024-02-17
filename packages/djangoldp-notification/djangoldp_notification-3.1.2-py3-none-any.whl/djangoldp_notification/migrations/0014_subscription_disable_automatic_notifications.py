# Generated by Django 2.2.23 on 2021-10-16 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_notification', '0013_auto_20211016_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='disable_automatic_notifications',
            field=models.BooleanField(default=False, help_text='By default, notifications will be sent to this inbox everytime the target object/container is updated. Setting this flag to true prevents this behaviour, meaning that notifications will have to be triggered manually'),
        ),
    ]
