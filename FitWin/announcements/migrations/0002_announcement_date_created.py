# Generated by Django 4.1.7 on 2023-03-31 15:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='date_created',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2023, 3, 31, 15, 21, 8, 315285, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]