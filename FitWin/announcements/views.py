from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import HttpResponse, redirect, render
from django.template import loader
from django.utils import timezone
from users.models import User, is_client, is_trainer

from .gcalendar import CalendarAPI
from .models import Announcement, Category


def validate_dates(start_date, finish_date):
    now_date = (datetime.now() + timedelta(hours=1))
    val = False
    if (now_date > start_date or start_date > finish_date):
        val = True
    return val


def validate_capacity(capacity):
    val = False
    capacity = int(capacity)
    if capacity <= 0:
        val = True
    return val


def validate_price(price):
    val = False
    price = float(price)
    if price <= 0.0:
        val = True
    return val


def validate_announcement(request, trainer, title, description, place, price, capacity,
                          day, start_date, finish_date):
    errors = False

    if validate_capacity(capacity):
        errors = True
        messages.error(request, "La capacidad no puede ser 0")
    if validate_price(price):
        errors = True
        messages.error(
            request, "El precio no puede ser menor o igual que cero")
    if title == '' or description == '' or place == '' or price == '' \
            or capacity == '' or day == '' or start_date == '' or finish_date == '':
        errors = True
        messages.error(request, "Todos los datos son obligatorios")
    if errors == False:
        start_date = datetime.strptime(start_date, '%H:%M').time()
        finish_date = datetime.strptime(finish_date, '%H:%M').time()
        day = datetime.strptime(day, '%Y-%m-%d').date()
        start_date = datetime.combine(day, start_date)
        finish_date = datetime.combine(day, finish_date)

        if validate_dates(start_date, finish_date):
            errors = True
            messages.error(request, "Las fechas son incorrectas")

    return errors


@login_required
@user_passes_test(is_trainer)
def create_announcement(request):
    if request.method == 'POST':
        trainer = request.user
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        place = request.POST.get('place', 'No definido')
        price = request.POST.get('price', '0.0')
        capacity = request.POST.get('capacity', '0')
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')

        errors = validate_announcement(request, title, description, place, price,
                                       capacity, day, start_date, finish_date)

        if not trainer.is_premium and trainer.num_announcements >= 5:
            errors = True
            messages.error(
                request, "Ha alcanzado el número máximo de anuncios permitidos como usuario Free")

        if errors == True:
            template = loader.get_template("form.html")
            context = {}
            return HttpResponse(template.render(context, request))
        else:
            capacity = int(capacity)
            price = float(price)

            calendar = CalendarAPI(request.user)
            calendar.create_calendar()
            event_id = calendar.create_event(title, description, start_date.isoformat(),
                                             finish_date.isoformat())

            announcement = Announcement()
            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity
            announcement.trainer = trainer
            announcement.start_date = start_date
            announcement.finish_date = finish_date
            announcement.google_calendar_event_id = event_id

            categories = list()

            announcement.save()
            announcement.categories.set(categories)

            trainer.num_announcements += 1
            trainer.save()

            return redirect('/trainers')
    elif request.method == 'GET':
        template = loader.get_template("form.html")
        context = {}
        return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_trainer)
def edit_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    trainer = request.user

    now = timezone.now()
    if announcement.finish_date < now:
        messages.error(
            request, "No se puede editar este anuncio porque ya ha finalizado.")
        return redirect('/announcements/list?trainerId=' + trainer.id)

    if announcement.trainer.id != trainer.id:
        messages.error(
            request, "No se puede editar los anuncios de otros entrenadores.")
        return redirect('/announcements/list?trainerId=' + trainer.id)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        place = request.POST.get('place', '')
        price = request.POST.get('price', '')
        capacity = request.POST.get('capacity', '0')
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')

        errors = validate_announcement(request, trainer, title, description, place, price,
                                       capacity, day, start_date, finish_date)

        if errors == True:
            return redirect("/announcements/edit/"+str(announcement.id))
        else:
            calendar = CalendarAPI(request.user)
            calendar.edit_event(announcement.google_calendar_event_id, title, description,
                                start_date.isoformat(), finish_date.isoformat())

            capacity = int(capacity)
            price = float(price)
            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity
            announcement.start_date = timezone.make_aware(start_date)
            finish_date = timezone.make_aware(finish_date)
            announcement.finish_date = finish_date
            announcement.save()
            return redirect('/trainers')
    elif request.method == 'GET':
        template = loader.get_template("form.html")
        context = {
            'a': announcement
        }
        return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_trainer)
def delete_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    announcement.delete()

    calendar = CalendarAPI(announcement.trainer)
    calendar.delete_event(announcement.google_calendar_event_id)

    messages.success(request, 'El anuncio ha sido eliminado correctamente.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@user_passes_test(is_trainer)
def add_categories(request, announcement_id):
    if request.method == 'POST':
        category_name = request.POST.get('category', '')
        category = Category.objects.get(name=category_name)
        categories = list()
        categories.append(category.id)
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.categories.add(category.id)
        announcement.save()
        url = '/announcements/add-categories/'+str(announcement_id)
        return redirect(url)
    elif request.method == 'GET':
        announcement = Announcement.objects.get(id=announcement_id)
        categories = Category.objects.all()
        template = loader.get_template("add_categories.html")
        context = {'categories': categories, 'a': announcement}
        return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_trainer)
def delete_categories(request, announcement_id, category_id):
    announcement = Announcement.objects.get(id=announcement_id)
    category = Category.objects.get(id=category_id)
    announcement.categories.remove(category)
    return redirect("/announcements/add-categories/"+str(announcement_id))


@login_required
@user_passes_test(is_client)
def book_announcement(request, announcement_id):
    client = request.user
    announcement = Announcement.objects.get(id=announcement_id)

    if announcement.capacity > 0 and client not in announcement.clients.all():
        announcement.clients.add(client.id)
        announcement.capacity = announcement.capacity - 1
        announcement.save()

        calendar = CalendarAPI(announcement.trainer)
        calendar.add_attendee_to_event(
            announcement.google_calendar_event_id, client)

        messages.success(request, "¡Reserva realizada con éxito!")
    else:

        messages.error(
            request, "No hay suficiente capacidad para reservar esta clase o ya esta apuntado a esta clase")

    return redirect('/announcements/list_client_announcements', announcement_id=announcement.id)


@login_required
@user_passes_test(is_client)
def cancel_book_announcement(request, announcement_id):
    client = request.user
    announcement = Announcement.objects.get(id=announcement_id)
    if client in announcement.clients.all():
        announcement.clients.remove(client.id)
        announcement.capacity = announcement.capacity + 1
        announcement.save()

        calendar = CalendarAPI(announcement.trainer)
        calendar.remove_attendee_from_event(
            announcement.google_calendar_event_id, client)
    else:
        messages.error(request, "Aún no estas inscrito a esta clase")
    return redirect("/announcements/list_client_announcements")


def announcement_details(request, announcement_id):
    announcement = Announcement.objects.filter(id=announcement_id).first()
    if not announcement:
        messages.error(request, "El anuncio no existe.")
        return redirect('announcement_list')

    context = {
        'announcement': announcement,
    }
    return render(request, 'announcement_details.html', context)


def list_announcements(request):
    user = request.user
    n_announcements = request.GET.get('nAnnouncements', 25)
    page_number = request.GET.get('page', 1)

    sort_by = request.GET.get('sortBy', 'bestRated')
    trainer_id = request.GET.get('trainerId', None)
    category = request.GET.get('category', None)
    show_full = request.GET.get('showFull', None) == 'True'
    show_booked = request.GET.get('showBooked', None) == 'True'
    min_price = request.GET.get('minPrice', None)
    max_price = request.GET.get('maxPrice', None)
    min_rating = request.GET.get('minRating', None)

    categories = Category.objects.order_by('name').annotate(
        announcement_count=Count('announcement'))

    announcements = Announcement.objects.all()
    announcements = sort_announcements(announcements, sort_by)
    announcements = filter_announcements(
        announcements, user, trainer_id, category, show_full, show_booked, min_price, max_price, min_rating)
    announcements_count = announcements.count()

    paginator = Paginator(announcements, n_announcements)
    page_obj = paginator.get_page(page_number)

    context = {
        'announcements': page_obj,
        'announcements_count': announcements_count,
        'categories': categories,
        'page_obj': page_obj,
        'page_number': page_number,
        'n_announcements': n_announcements,
    }

    return render(request, 'list_announcements.html', context)


def sort_announcements(announcements, sort_by):
    if sort_by == 'bestRated':
        announcements = announcements.order_by('-trainer__avg_rating')
    elif sort_by == 'recommended':
        # TODO
        pass
    elif sort_by == 'priceAsc':
        announcements = announcements.order_by('price')
    elif sort_by == 'priceDesc':
        announcements = announcements.order_by('-price')
    return announcements


def filter_announcements(announcements, user, trainer_id, category, show_full,
                         show_booked, min_price, max_price, min_rating):
    if trainer_id is not None and trainer_id != '':
        if User.objects.filter(id=trainer_id).exists():
            trainer = User.objects.get(id=trainer_id)
            announcements = announcements.filter(trainer=trainer)

    if category is not None and category != '':
        announcements = announcements.filter(categories__in=[category])

    if show_full:
        announcements = announcements.filter(capacity=0)

    if show_booked:
        if is_client(user):
            announcements = announcements.filter(clients__id=user.id)

    if min_price is not None and min_price != '':
        announcements = announcements.filter(price__gte=min_price)

    if max_price is not None and max_price != '':
        announcements = announcements.filter(price__lte=max_price)

    if min_rating is not None and min_rating != '':
        announcements = announcements.filter(
            trainer__avg_rating__gte=min_rating)

    return announcements
