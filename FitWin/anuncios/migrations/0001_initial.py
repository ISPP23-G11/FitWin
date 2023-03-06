# Generated by Django 4.1.7 on 2023-03-03 09:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Anuncio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Titulo')),
                ('description', models.TextField(verbose_name='Descripcion')),
                ('place', models.CharField(max_length=250, verbose_name='Lugar')),
                ('price', models.FloatField()),
                ('capacity', models.IntegerField()),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')),
                ('finish_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de fin')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Anuncio',
                'verbose_name_plural': 'Anuncios',
            },
        ),
    ]