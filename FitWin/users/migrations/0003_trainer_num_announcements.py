# Generated by Django 4.1.7 on 2023-04-05 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_trainer_date_premium_trainer_is_premium'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainer',
            name='num_announcements',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
