from django.shortcuts import render
from announcements.models import Announcement, Category

def search_announcements(request):
    # Obtener los datos del formulario
    category = request.GET.get('category')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    title = request.GET.get('title')
    description = request.GET.get('description')
    place = request.GET.get('place')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Convertir las cadenas de fecha y hora en objetos datetime
    start_date = parse_datetime(start_date_str) if start_date_str else None
    end_date = parse_datetime(end_date_str) if end_date_str else None

    # Crear un diccionario para almacenar los filtros
    filters = {}

    # Agregar los filtros según los valores proporcionados
    if category:
        filters['categories__pk'] = category
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

    # Realizar la consulta a la base de datos
    announcements = Announcement.objects.filter(**filters)

    # Obtener todas las categorías para mostrar en el formulario
    categories = Category.objects.all()

    # Renderizar el template
    return render(request, 'search.html', {'announcements': announcements, 'categories': categories})
