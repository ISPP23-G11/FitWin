from django.shortcuts import render
from django.contrib.auth import login as login_django
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect
from django.template import loader
from users.models import Trainer, Client 
from django.views.generic import View
from .forms import SignUpForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

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


        

def trainer_register(request):
     if request.method == 'POST':
          form = SignUpForm(request.POST)

          if form.is_valid():
               
               post_save.connect(create_trainer_profile, sender=User)
               post_save.connect(save_trainer_profile, sender=User)
               
               form.save()

               username = form.cleaned_data['username']
               messages.success(request, f'Usuario {username} creado')
               return redirect('/')
     else:
          form=SignUpForm()

     context = { 'form' : form }
     return render(request, 'account/trainerRegister.html', context)

def client_register(request):
     if request.method == 'POST':
          form = SignUpForm(request.POST)

          if form.is_valid():
               
               post_save.connect(create_client_profile, sender=User)
               post_save.connect(save_client_profile, sender=User)
               
               form.save()
   
               username = form.cleaned_data['username']
               messages.success(request, f'Usuario {username} creado')
               return redirect('/')
     else:
          form=SignUpForm()

     context = { 'form' : form }
     return render(request, 'account/clientRegister.html', context)
        

        
def create_client_profile(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance)


def save_client_profile(sender, instance, **kwargs):
    instance.client.save()


def create_trainer_profile(sender, instance, created, **kwargs):
    if created:
        Trainer.objects.create(user=instance)

def save_trainer_profile(sender, instance, **kwargs):
    instance.trainer.save()



