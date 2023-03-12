from django.db import models
from users.models import Trainer, Client

class Category(models.Model):
    DIFFICULTY = 'difficulty'
    OBJECTIVES = 'objectives'
    RECOVERY = 'recovery'
    TYPE_CHOICES = (
        (DIFFICULTY, 'Difficulty'),
        (OBJECTIVES, 'Objectives'),
        (RECOVERY, 'Recovery'),
    )
    name=models.CharField(max_length=250, verbose_name='Categoria')
    types=models.CharField(max_length=20, choices=TYPE_CHOICES, default=DIFFICULTY)
    

    

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=250, verbose_name='Titulo')
    description = models.TextField(verbose_name='Descripcion')
    place = models.CharField(max_length=250, verbose_name='Lugar')
    price=models.FloatField()
    capacity=models.IntegerField()
    trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)
    clients=models.ManyToManyField(Client, blank=True)
    categories=models.ManyToManyField(Category, blank=True)
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')
    finish_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de fin')
    invitation_sent = models.BooleanField(default=False)
    google_calendar_event_id = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return self.title
    

