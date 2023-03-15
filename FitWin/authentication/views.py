from django.shortcuts import render
from django.contrib.auth import login as login_django
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect
from django.template import loader
from users.models import Trainer, Client 

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_django(request, user)
            trainer = Trainer.objects.filter(user = user)
            client = Client.objects.filter(user = user)
            if trainer:
                return redirect('/trainers')
            elif client:
                return redirect('/clients')
    else:
        template = loader.get_template("account/login.html") 
        context = {}
        return HttpResponse(template.render(context, request))
