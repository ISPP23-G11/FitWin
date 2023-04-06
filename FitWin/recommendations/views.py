from django.shortcuts import render
from announcements.models import Announcement
from users.models import Client
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.

def is_client(user):
    return Client.objects.filter(user = user).exists()

@login_required
@user_passes_test(is_client)
@cache_page(60*5) #Cache durante 5 minutos
def view_recommended(request):
    user = request.user
    client = Client.objects.filter(user = user).get()
    announcements = list(get_recommendations(client))
    return render(request, 'recommended.html', {'announcements': announcements})


def get_similar_users(self:Client):
        client_ads = Announcement.objects.filter(clients=self)
        print(len(client_ads))
        other_clients = Client.objects.exclude(pk=self.pk)
        common_ads = set()
        for client in other_clients:
            ads = set(Announcement.objects.filter(clients=client))
            common_ads.update(ads.intersection(client_ads))
        similarities = []
        for client in other_clients:
            ads = set(Announcement.objects.filter(clients=client))
            common_client_ads = ads.intersection(common_ads)
            similarity = len(common_client_ads)/len(common_ads) if len(common_ads) > 0 else 0
            #Al menos que haya un 40% de anuncios en comun con otros usuarios
            if similarity >= 0.4:
                similarities.append((client, similarity))
        similarities.sort(key=lambda x: x[1],reverse=True)
        return similarities[:15]


def get_recommendations(self:Client):
    similar_users = get_similar_users(self)
    recommended_adds = set()
    for user,similarity in similar_users:
        print(f'Afinidad de usuario {user}:\t{similarity}')
        user_ads = Announcement.objects.filter(clients=user).exclude(clients=self)
        recommended_adds.update(user_ads)
        for ad in user_ads:
            similar_ads = ad.get_similar()
            recommended_adds.update([x for x,_ in similar_ads if x not in Announcement.objects.filter(clients=self)])
    return recommended_adds