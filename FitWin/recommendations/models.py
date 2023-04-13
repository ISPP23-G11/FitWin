from django.db import models

# Create your models here.
from announcements.models import Announcement
from users.models import User
class Recommendation(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    score = models.FloatField()
    client = models.ForeignKey(User, on_delete=models.CASCADE)

def create_similarities(client:User):
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

def run_create_similarities():
    # Obtiene todos los usuarios y ejecuta la función create_similarities para cada uno de ellos
    users = User.objects.filter(role="client")
    for user in users:
        create_similarities(user)

