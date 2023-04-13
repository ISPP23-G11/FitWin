from django.db import models
from users.models import User, get_average_ratings


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
    price = models.FloatField()
    capacity = models.IntegerField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="announcement_trainer")
    clients = models.ManyToManyField(User, blank=True, related_name="announcement_client")
    categories = models.ManyToManyField(Category, blank=True)
    start_date = models.DateTimeField(auto_now_add=False, verbose_name='Fecha de inicio')
    finish_date = models.DateTimeField(auto_now_add=False, verbose_name='Fecha de fin')
    date_created = models.DateField(auto_now_add=True)
    invitation_sent = models.BooleanField(default=False)
    google_calendar_event_id = models.CharField(max_length=120, blank=True, null=True)

    def get_similarity(self, announcement):
        categories_similarities = len(set(self.categories.all()).intersection(set(announcement.categories.all()))) / len(set(self.categories.all()) | set(announcement.categories.all()))
            #Se considera precio similar a aquellos grupos que difieran de 5 en 5 euros
        price_similarity = 1 / (1 + abs(self.price - announcement.price)/5)
        place_similarity = sum(a==b for a,b in zip(self.place,announcement.place)) / min(len(self.place),len(announcement.place))
        trainer_similarity = 1 if self.trainer == announcement.trainer else 0.5
        trainer_recomendation =  get_average_ratings(announcement.trainer)
        trainer_weight = 2/3 if announcement.trainer.date_premium is not None else 0 #Esta parte esta por implementar
        similarity = 10*(0.5*categories_similarities+0.15 * price_similarity +0.05* place_similarity +0.3* (trainer_similarity + trainer_recomendation/5 + trainer_weight)/2)
            #Criterios de aceptacion: 
            #Esperado al menos 1/3 de categorias similares
            #Esperado al menos 1/2 de similaridad respecto al precio
            #Esperado al menos 1/4 de similaridad respecto al lugar
            #Aplicando la formula respecto a entrenador sin rating y distinto al anuncio con el que se compara:
            # 10*(0.5*1/3+0.15*1/2+0.05*1/4+0.3*1/4) = 3.29 ----> Se aceptan anuncios a partir de similitud = 3.5 para ser estrictos
        return similarity

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return self.title
    
class Calendar(models.Model):
    google_calendar_id = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
