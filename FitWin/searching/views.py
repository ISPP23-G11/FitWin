from django.shortcuts import render
from announcements.models import Announcement, Category
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Client
from django.views.decorators.cache import cache_page

def is_client(user):
    return Client.objects.filter(user = user).exists()

@login_required
@user_passes_test(is_client)
@cache_page(60*2)
def search_announcements(request):
    # Obtener los datos del formulario
    category_diff = request.GET.get('category_difficulty')
    category_obj = request.GET.get('category_objective')
    category_rec = request.GET.get('category_recovery')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    title = request.GET.get('title')
    description = request.GET.get('description')
    place = request.GET.get('place')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    trainer = request.GET.get('trainer')

    # Convertir las cadenas de fecha y hora en objetos datetime
    start_date = parse_datetime(start_date_str) if start_date_str else None
    end_date = parse_datetime(end_date_str) if end_date_str else None

    # Crear un diccionario para almacenar los filtros
    filters = {}

    # Agregar los filtros según los valores proporcionados
    if category_diff:
        filters.setdefault('categories__pk__in', []).append(category_diff)
    if category_obj:
        filters.setdefault('categories__pk__in', []).append(category_obj)
    if category_rec:
        filters.setdefault('categories__pk__in', []).append(category_rec)
    if start_date:
        filters['start_date__gte'] = start_date
    if end_date:
        filters['finish_date__lte'] = end_date
    if title:
        filters['title__icontains'] = title
    if description:
        filters['description__icontains'] = description
    if place:
        filters['place__icontains'] = place
    if min_price:
        filters['price__gte'] = float(min_price)
    if max_price:
        filters['price__lte'] = float(max_price)
    if trainer:
        filters['trainer__user__username__icontains'] = trainer

    # Realizar la consulta a la base de datos
    announcements = Announcement.objects.filter(**filters).distinct()

    # Obtener todas las categorías para mostrar en el formulario
    categories = Category.objects.all()

    user = request.user
    client = Client.objects.filter(user = user).get()
    recommended = list(get_recommendations(client))

    # Renderizar el template
    return render(request, 'search.html', {'announcements': announcements, 'categories': categories, 'recommended':recommended})

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