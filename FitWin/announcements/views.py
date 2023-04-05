from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, redirect, render
from django.template import loader
from django.utils.timezone import make_aware
from users.models import User, is_client, is_trainer

from .gcalendar import CalendarAPI
from .models import Announcement, Category


def validate_dates(start_date, finish_date):
    now_date = (datetime.now()+ timedelta(hours=1))
    val = False
    if( now_date > start_date or start_date > finish_date):
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

@login_required
@user_passes_test(is_trainer)
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        place = request.POST.get('place', 'No definido')
        price = request.POST.get('price', '0.0')
        capacity = request.POST.get('capacity', '0')
        trainer = request.user
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')
        errors = False

        if validate_capacity(capacity):
            errors = True
            messages.error(request, "La capacidad no puede ser 0")
        if validate_price(price):
            errors = True
            messages.error(request, "El precio no puede ser menor o igual que cero")
        if title == '' or description == '' or place == '' or price == '' or capacity == '' or day == '' or start_date == '' or finish_date == '':
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

        if errors == True:
            template = loader.get_template("form.html")
            context = {}
            return HttpResponse(template.render(context, request))

        else:
            capacity = int(capacity)
            price = float(price)

            calendar = CalendarAPI(request.user)
            calendar.create_calendar()
            event_id = calendar.create_event(title,description,start_date.isoformat(),
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
            return redirect('/trainers')
    elif request.method == 'GET':
        template = loader.get_template("form.html")

        context = {}
        return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_trainer)
def edit_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id = announcement_id)
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        place = request.POST.get('place', '')
        price = request.POST.get('price', '')
        capacity = request.POST.get('capacity', '0')
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')

        errors = False
        if validate_price(price):
            errors = True
            messages.error(request, "El precio no puede ser menor o igual que cero")
        if title == '' or description == '' or place == '' or price == '' or capacity == '' or day == '' or start_date == '' or finish_date == '':
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

        if errors == True:
            return redirect("/announcements/edit/"+str(announcement.id))

        else:
            capacity = int(capacity)
            price = float(price)

            calendar = CalendarAPI(request.user)
            calendar.edit_event(announcement.google_calendar_event_id, title, description,
                                start_date.isoformat(), finish_date.isoformat())

            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity
            announcement.start_date = make_aware(start_date)
            finish_date = make_aware(finish_date)
            announcement.finish_date = finish_date
            announcement.save()
            return redirect('/trainers')
    elif request.method == 'GET':
        template = loader.get_template("form.html")
        context = {'a':announcement}
        return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_trainer)
def list_own_all(request):
    trainer = User.objects.get(id=request.user.id)
    announcements = Announcement.objects.filter(trainer=trainer)

    paginator = Paginator(announcements, 2)  # muestra 2 elementos por página


    page = request.GET.get('page')
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        page = 1  # establecer el valor predeterminado de la página en 1
        announcements = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages  # establecer la página en la última página disponible
        announcements = paginator.page(page)

    return render(request, 'list_announcements.html', {'announcements': announcements})

@login_required
@user_passes_test(is_trainer)
def list_max_capacity_announcements(request):
    trainer = User.objects.get(id=request.user.id)
    announcements = Announcement.objects.filter(trainer=trainer).annotate(client_count=Count('clients')).filter(capacity=F('client_count'))

    paginator = Paginator(announcements, 2)

    page = request.GET.get('page')
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        announcements = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        announcements = paginator.page(page)

    return render(request, 'list_max_capacity_announ.html', {'announcements': announcements})

@login_required
@user_passes_test(is_trainer)
def delete_announce(request, announcement_id):
    announcement = Announcement.objects.get(id = announcement_id)
    announcement.delete()

    calendar = CalendarAPI(announcement.trainer.user)
    calendar.delete_event(announcement.google_calendar_event_id)

    messages.success(request, 'El anuncio ha sido eliminado correctamente.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@user_passes_test(is_trainer)
def add_categories(request, announcement_id):
    if request.method == 'POST':
        category_name = request.POST.get('category', '')
        category = Category.objects.get(name = category_name)
        categories = list()
        categories.append(category.id)
        announcement = Announcement.objects.get(id = announcement_id)
        announcement.categories.add(category.id)
        announcement.save()
        url = '/announcements/add-categories/'+str(announcement_id)
        return redirect(url)
    elif request.method == 'GET':
        announcement = Announcement.objects.get(id = announcement_id)
        categories = Category.objects.all()
        template = loader.get_template("add_categories.html")
        context = {'categories':categories, 'a':announcement}
        return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_trainer)
def delete_categories(request, announcement_id, category_id):
    announcement = Announcement.objects.get(id = announcement_id)
    category = Category.objects.get(id = category_id)
    announcement.categories.remove(category)
    return redirect("/announcements/add-categories/"+str(announcement_id))


@login_required
@user_passes_test(is_client)
def book_announcement(request, announcement_id):
    client = User.objects.get(id=request.user.id)
    announcement = Announcement.objects.get(id=announcement_id)

    if announcement.capacity > 0 and client not in announcement.clients.all():
        announcement.clients.add(client.id)
        announcement.capacity = announcement.capacity - 1
        announcement.save()  # Guarda el modelo Announcement actualizado

        calendar = CalendarAPI(announcement.trainer.user)
        calendar.add_attendee_to_event(announcement.google_calendar_event_id, client)

        messages.success(request, "¡Reserva realizada con éxito!")
    else:

        messages.error(request, "No hay suficiente capacidad para reservar esta clase o ya esta apuntado a esta clase")


    return redirect('/announcements/list_client_announcements', announcement_id=announcement.id)


@login_required
@user_passes_test(is_client)
def cancel_book_announcement(request, announcement_id):
    client = User.objects.get(user = request.user)
    announcement = Announcement.objects.get(id = announcement_id)
    if client in announcement.clients.all():
        announcement.clients.remove(client.id)
        announcement.capacity = announcement.capacity + 1
        announcement.save()

        calendar = CalendarAPI(announcement.trainer.user)
        calendar.remove_attendee_from_event(announcement.google_calendar_event_id, client)
    else:
        messages.error(request, "Aún no estas inscrito a esta clase")
    return redirect("/announcements/list_client_announcements")


@login_required
@user_passes_test(is_client)
def list_client_announcements(request):
    client_announcements = Announcement.objects.filter(id=request.user.id)

    paginator = Paginator(client_announcements,3)

    page = request.GET.get('page')
    try:
        client_announcements = paginator.page(page)
    except PageNotAnInteger:
        page = 1  # establecer el valor predeterminado de la página en 1
        client_announcements = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages  # establecer la página en la última página disponible
        client_announcements = paginator.page(page)

    return render(request, "list_client_announcements.html", {'client_announcements': client_announcements})


def list_announcements(request):
    announcements = Announcement.objects.all()

    paginator = Paginator(announcements, 4)  # muestra 4 elementos por página

    page = request.GET.get('page')
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        page = 1  # establecer el valor predeterminado de la página en 1
        announcements = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages  # establecer la página en la última página disponible
        announcements = paginator.page(page)

    return render(request, 'list_all_announcements.html', {'announcements': announcements})


@login_required
@user_passes_test(is_client)
def show_his_announcements(request, trainer_id):
    trainer = User.objects.get(id = trainer_id)
    announcements = Announcement.objects.filter(trainer=trainer)
    client = User.objects.get(user = request.user)

    paginator = Paginator(announcements, 2)  # muestra 2 elementos por página

    page = request.GET.get('page')
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        page = 1  # establecer el valor predeterminado de la página en 1
        announcements = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages  # establecer la página en la última página disponible
        announcements = paginator.page(page)

    return render(request, 'list_announcements_trainers.html', {'announcements': announcements, 'trainer':trainer, 'client':client})

@login_required
def handler_announcement_details(request, announcement_id):
    context = {}
    announcement = Announcement.objects.filter(id=announcement_id).first()
    if not announcement:
        messages.error(request, "El anuncio no existe.")
        return redirect('announcement_list')
    context['announcement'] = announcement
    return render(request, 'announcement_details.html', context)