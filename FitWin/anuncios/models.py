from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Trainer(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)


class Client(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)

class Category(models.Model):

    LOSE_WEIGHT = 'LW'
    MUSCLE_MASS = 'MM'
    CROSSFIT = 'CF'
    PILATES = 'PL'
    BOXING = 'BX'
    AEROBIC = 'AB'
    MARTIAL_ARTS = 'MA'
    

    CATEGORIES=[
        (LOSE_WEIGHT, 'Lose weight'),
        (MUSCLE_MASS, 'Muscle mass'),
        (CROSSFIT, 'Crossfit'),
        (PILATES, 'Pilates'),
        (BOXING, 'Boxing'),
        (AEROBIC, 'Aerobic'),
        (MARTIAL_ARTS, 'Martial arts'),
    ]
    
    name=models.CharField(max_length=250, verbose_name='Categoria', choices=CATEGORIES, default=LOSE_WEIGHT)



class Announcement(models.Model):
    title = models.CharField(max_length=250, verbose_name='Titulo')
    description = models.TextField(verbose_name='Descripcion')
    place = models.CharField(max_length=250, verbose_name='Lugar')
    price=models.FloatField()
    capacity=models.IntegerField()
    trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)
    clients=models.ManyToManyField(Client)
    categories=models.ManyToManyField(Category)
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')
    finish_date = models.DateTimeField(auto_now=True, verbose_name='Fecha de fin')

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return self.title
    

