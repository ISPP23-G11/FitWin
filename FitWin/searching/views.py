from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from announcements.models import Announcement, Category
from users.models import is_client
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(is_client)
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
    min_capacity = request.GET.get('min_capacity')
    max_capacity = request.GET.get('max_capacity')

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
    if min_capacity:
        filters['capacity__gte'] = int(min_capacity)
    if max_capacity:
        filters['capacity__lte'] = int(max_capacity)


    # Realizar la consulta a la base de datos
    announcements = Announcement.objects.filter(**filters).distinct()

    # Obtener todas las categorías para mostrar en el formulario
    categories = Category.objects.all()

    # Renderizar el template
    return render(request, 'search.html', {'announcements': announcements, 'categories': categories})
