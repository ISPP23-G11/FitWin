# Generated by Django 4.1.7 on 2023-03-17 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_client_birthday_alter_trainer_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trainer',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
    ]