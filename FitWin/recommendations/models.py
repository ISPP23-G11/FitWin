from django.db import models
from datetime import timedelta
from django.utils import timezone

# Create your models here.
from announcements.models import Announcement
from users.models import User
class Recommendation(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    score = models.FloatField()
    client = models.ForeignKey(User, on_delete=models.CASCADE)

def create_similarities(client:User):
    if not Announcement.objects.filter(clients=client).exists():
        return
    last_login = client.last_login
    if Recommendation.objects.filter(client=client).exists() and timezone.now() - last_login < timedelta(days=1):
        return
    if Recommendation.objects.filter(client=client).exists() and timezone.now() - last_login > timedelta(days=1):
        Recommendation.objects.filter(client=client).delete()
    client_announcements = Announcement.objects.filter(clients = client)
    announcements = Announcement.objects.exclude(pk__in=client_announcements.values_list('pk', flat=True))
    similarities = dict()
    for announce in client_announcements:
        for other_announce in announcements:
            similarity = announce.get_similarity(other_announce)
            if other_announce not in similarities.keys() or similarity > similarities.get(other_announce):
                similarities.update({other_announce:similarity})
    for item in similarities:
        recommendation = Recommendation(announcement=item,score=similarities.get(item),client=client)
        recommendation.save()

#Si se encuentra forma de hacerlo periodicamente utilizar esta funcion, sino quedarse con la solucion que esta
def run_create_similarities():
    # Obtiene todos los usuarios y ejecuta la función create_similarities para cada uno de ellos
    users = User.objects.filter(role="client")
    for user in users:
        create_similarities(user)

