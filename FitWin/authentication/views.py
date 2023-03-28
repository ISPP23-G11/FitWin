from django.shortcuts import render
from django.contrib.auth import login as login_django
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect
from django.template import loader
from users.models import User
from django.views.generic import View
from .forms import SignUpForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_django(request, user)
            trainer = User.objects.filter(user = user)
            client = User.objects.filter(user = user)
            if trainer:
                return redirect('/trainers')
            elif client:
                return redirect('/clients')
        else:
            messages.error(request, "El usuario y la contraseña son incorrectos")
            return redirect("/login")
    else:
        template = loader.get_template("account/login.html") 
        context = {}
        return HttpResponse(template.render(context, request))


def trainer_register(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        password_again = request.POST.get("password_again", "")
        bio = request.POST.get("bio", "")
        birthday = request.POST.get("birthday", "")
        picture = request.FILES["picture"]
        name = request.POST.get("name", "")
        last_name = request.POST.get("last_name", "")
        roles = ["trainer"]

        old_user = User.objects.filter(username = username)

        errors = False
        if old_user:
            errors = True
            messages.error(request, "Este nombre de usuario ya está cogido")

        if password != password_again:
            errors = True
            messages.error(request, "Las contraseñas no coinciden")

        if birthday!= "":
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
            if birthday >= datetime.now():
                errors = True
                messages.error(request, "La fecha del cumpleaños tiene que ser anterior a hoy")
        else:
            errors = True
            messages.error(request, "La fecha de naciemiento es obligatoria")

        if not errors:
            user = User.objects.create_user(username = username, password=password,
                                            email=email, first_name=name, last_name=last_name, roles=roles)
            user.save()
            trainer = User(user = user, bio=bio, birthday=birthday)
            trainer.picture.save(picture.name, picture)
            trainer.save()
            return redirect("/login")
        else:
            return redirect("/trainerRegister/")
    else:
        template = loader.get_template("account/trainerRegister.html") 
        context = {}
        return HttpResponse(template.render(context, request))

def client_register(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        password_again = request.POST.get("password_again", "")
        bio = request.POST.get("bio", "")
        birthday = request.POST.get("birthday", "")
        picture = request.FILES["picture"]
        name = request.POST.get("name", "")
        last_name = request.POST.get("last_name", "")
        roles = ["client"]

        old_user = User.objects.filter(username = username)

        errors = False
        if old_user:
            errors = True
            messages.error(request, "Este nombre de usuario ya está cogido")

        if password != password_again:
            errors = True
            messages.error(request, "Las contraseñas no coinciden")

        if birthday!= "":
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
            if birthday >= datetime.now():
                errors = True
                messages.error(request, "La fecha del cumpleaños tiene que ser anterior a hoy")
        else:
            errors = True
            messages.error(request, "La fecha de naciemiento es obligatoria")

        if not errors:
            user = User.objects.create_user(username = username, password=password,
                                            email=email, first_name=name, last_name=last_name, roles = roles)
            user.save()
            client = User(user = user, bio=bio, birthday=birthday)
            client.picture.save(picture.name, picture)
            client.save()
            return redirect("/login")
        else:
            return redirect("/clientRegister/")
    else:
        template = loader.get_template("account/clientRegister.html") 
        context = {}
        return HttpResponse(template.render(context, request))