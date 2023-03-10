from django.shortcuts import render
from django.contrib.auth import login as login_django
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect
from django.template import loader

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
