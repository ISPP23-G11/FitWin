from django.shortcuts import render
from django.contrib import messages
from .models import *
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

def validate_dates(start_date, finish_date):
    now_date = (datetime.now()+ timedelta(hours=1))
    val = False
    if( now_date > start_date or start_date > finish_date):
        val = True

    print(finish_date)
    return val

def validate_capacity(capacity):
    val = False
    if capacity <= 0:
        val = True
    return val


@login_required
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
        print(finish_date)
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
            announcement = Announcement()
            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity
            announcement.trainer = trainer
            announcement.start_date = start_date
            announcement.finish_date = finish_date

            categories = list()
            
            announcement.save()
            announcement.categories.set(categories)
            template = loader.get_template("main.html") 
            context = {}
            return HttpResponse(template.render(context, request))

    elif request.method == 'GET':
        template = loader.get_template("form.html") 
        context = {}
        return HttpResponse(template.render(context, request))
    
@login_required
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
        print(finish_date)

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
            print(finish_date)
            announcement.title = title
            announcement.description = description
            announcement.place = place
            announcement.price = price
            announcement.capacity = capacity - len(announcement.clients.all())
            announcement.start_date = make_aware(start_date)
            finish_date = make_aware(finish_date)
            print(finish_date)
            announcement.finish_date = finish_date
            announcement.save()
            print(announcement.finish_date)
            template = loader.get_template("main.html") 
            context = {}
            return HttpResponse(template.render(context, request))
    elif request.method == 'GET':
        template = loader.get_template("form.html") 
        context = {'a':announcement}
        return HttpResponse(template.render(context, request))


def main(request):
    template = loader.get_template("main.html") 
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_django(request, user)
            messages.error(request, "Usuario autenticado")
            return redirect('/')
    else:
        template = loader.get_template("login.html") 
        context = {}
        return HttpResponse(template.render(context, request))


def list_own_all(request):
    pass

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

def delete_categories(request, announcement_id, category_id):
    announcement = Announcement.objects.get(id = announcement_id)
    category = Category.objects.get(id = category_id)
    announcement.categories.remove(category)
    return redirect("/announcements/add-categories/"+str(announcement_id))


def book_announcement(request, announcement_id):
    client = Client.objects.get(user = request.user)
    announcement = Announcement.objects.get(id = announcement_id)
    if announcement.capacity > 0:
        announcement.clients.add(client.id)
        announcement.capacity = announcement.capacity - 1
        announcement.save()
    else:
        messages.error(request, "No hay hueco para reservar esta clase")
    return redirect("/") 


def cancel_book_announcement(request, announcement_id):
    client = Client.objects.get(user = request.user)
    announcement = Announcement.objects.get(id = announcement_id)
    if client in announcement.clients.all():
        announcement.clients.remove(client.id)
        announcement.capacity = announcement.capacity + 1
        announcement.save()
    else:
        messages.error(request, "Aún no estas inscrito a esta clase")
    return redirect("/") 
    