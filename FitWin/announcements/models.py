from django.db import models
from users.models import Trainer, Client, User

class Category(models.Model):
    name=models.CharField(max_length=250, verbose_name='Categoria')

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=250, verbose_name='Titulo')
    description = models.TextField(verbose_name='Descripcion')
    place = models.CharField(max_length=250, verbose_name='Lugar')
    price = models.FloatField()
    capacity = models.IntegerField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    start_date = models.DateTimeField(auto_now_add=False, verbose_name='Fecha de inicio')
    finish_date = models.DateTimeField(auto_now_add=False, verbose_name='Fecha de fin')
    invitation_sent = models.BooleanField(default=False)
    google_calendar_event_id = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return self.title
    
class Calendar(models.Model):
    google_calendar_id = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
