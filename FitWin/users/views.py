from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Trainer, Client
from django.template import loader
from django.shortcuts import HttpResponse, redirect
from django.contrib import messages

def is_trainer(user):
    return Trainer.objects.filter(user = user).exists()

def is_client(user):
    return Client.objects.filter(user = user).exists()

@login_required
@user_passes_test(is_trainer)
def handler_trainers(request):
    user = request.user
    trainer = Trainer.objects.filter(user = user)
    if trainer:
        context = {}
        template = loader.get_template("main_trainers.html") 
        return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_client)
def handler_clients(request):
    user = request.user
    client = Client.objects.filter(user = user)
    if client:
        context = {}
        template = loader.get_template("main_clients.html") 
        return HttpResponse(template.render(context, request))

@login_required
def handler_client_details(request, client_id):
    client = Client.objects.filter(id = client_id)
    if client:
        client = client.get()
    else:
        messages.error(request, "No se ha encontrado al cliente")
    context = {'client':client}
    template = loader.get_template("client_details.html") 
    return HttpResponse(template.render(context, request))
