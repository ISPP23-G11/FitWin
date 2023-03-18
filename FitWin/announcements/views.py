from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import *
from users.models import Trainer, Client
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import HttpResponse, redirect
from datetime import datetime, timedelta
from django.contrib.auth import login as login_django
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Count
from django.http import HttpResponseRedirect
from .gcalendar import CalendarAPI

def validate_dates(start_date, finish_date):
    now_date = (datetime.now()+ timedelta(hours=1))
    val = False
    if( now_date > start_date or start_date > finish_date):
        val = True
    return val

def validate_capacity(capacity):
    val = False
    if capacity <= 0:
        val = True
    return val

def is_trainer(user):
    return Trainer.objects.filter(user = user).exists()

def is_client(user):
    return Client.objects.filter(user = user).exists()

@login_required
@user_passes_test(is_trainer)
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        place = request.POST.get('place', 'No definido')
        price = request.POST.get('price', '0.0')
        capacity = request.POST.get('capacity', '0')
        user = request.user
        trainer = Trainer.objects.get(user = user)
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')

        start_date = datetime.strptime(start_date, '%H:%M').time()
        finish_date = datetime.strptime(finish_date, '%H:%M').time()
        day = datetime.strptime(day, '%Y-%m-%d').date()

        start_date = datetime.combine(day, start_date)
        finish_date = datetime.combine(day, finish_date)

        capacity = int(capacity)
        price = float(price)

        errors = False

        if validate_dates(start_date, finish_date):
            errors = True
            messages.error(request, "Las fechas son incorrectas")
        if validate_capacity(capacity):
            errors = True
            messages.error(request, "La capacidad no puede ser 0")

        if errors == True:
            template = loader.get_template("form.html") 
            context = {}
            return HttpResponse(template.render(context, request))

        else:
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
            return redirect('/')
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
        place = request.POST.get('place', 'No definido')
        price = request.POST.get('price', '0.0')
        capacity = request.POST.get('capacity', '0')
        day = request.POST.get('day', '')
        start_date = request.POST.get('start_date', '')
        finish_date = request.POST.get('finish_date', '')

        start_date = datetime.strptime(start_date, '%H:%M').time()
        finish_date = datetime.strptime(finish_date, '%H:%M').time()
        
        day = datetime.strptime(day, '%Y-%m-%d').date()

        start_date = datetime.combine(day, start_date)
        finish_date = datetime.combine(day, finish_date)

        capacity = int(capacity)
        price = float(price)

        errors = False

        if validate_dates(start_date, finish_date):
            errors = True
            messages.error(request, "Las fechas son incorrectas")
        if validate_capacity(capacity):
            errors = True
            messages.error(request, "La capacidad no puede ser 0")

        if errors == True:
            return redirect("/announcements/edit/"+str(announcement.id))

        else:
            calendar = CalendarAPI(request.user)
            calendar.edit_event(announcement.google_calendar_event_id, title, description,
                                start_date.isoformat(), finish_date.isoformat())

            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity - len(announcement.clients.all())
            announcement.start_date = make_aware(start_date)
            finish_date = make_aware(finish_date)
            announcement.finish_date = finish_date
            announcement.save()
            return redirect('/')
    elif request.method == 'GET':
        template = loader.get_template("form.html") 
        context = {'a':announcement}
        return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_trainer)
def list_own_all(request):
    trainer = Trainer.objects.get(user=request.user)
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
    trainer = Trainer.objects.get(user=request.user)
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
    client = Client.objects.get(user = request.user)
    announcement = Announcement.objects.get(id = announcement_id)
    if announcement.capacity > 0:
        announcement.clients.add(client.id)
        announcement.capacity = announcement.capacity - 1
        announcement.save()

        calendar = CalendarAPI(announcement.trainer.user)
        calendar.add_attendee_to_event(announcement.google_calendar_event_id, client.user)
    else:
        messages.error(request, "No hay hueco para reservar esta clase")
    return redirect("/") 

@login_required
@user_passes_test(is_client)
def cancel_book_announcement(request, announcement_id):
    client = Client.objects.get(user = request.user)
    announcement = Announcement.objects.get(id = announcement_id)
    if client in announcement.clients.all():
        announcement.clients.remove(client.id)
        announcement.capacity = announcement.capacity + 1
        announcement.save()

        calendar = CalendarAPI(announcement.trainer.user)
        calendar.remove_attendee_from_event(announcement.google_calendar_event_id, client.user)
    else:
        messages.error(request, "Aún no estas inscrito a esta clase")
    return redirect("/") 

@login_required
@user_passes_test(is_client)
def list_client_announcements(request):
    context = {}
    template = loader.get_template("list_client_announcements.html") 
    return HttpResponse(template.render(context, request))