from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Trainer, Client, Rating, Comment
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

@login_required
@user_passes_test(is_client)
def rating_trainer(request, trainer_id):
    if request.method == 'POST':
        client = Client.objects.filter(user = request.user)
        trainer = Trainer.objects.filter(id = trainer_id)
        rating = request.POST.get('rating', '0')

        if not client or not trainer:
            messages.error(request, "El cliente o el entrenador no existen")

        if rating == '':
            messages.error(request, "No se ha seleccionado puntuación")
        elif int(rating) < 0:
            messages.error(request, "No se pueden dar puntuaciones negativas")
        else: 
            client = client.get()
            trainer = trainer.get()
            rating_object = Rating.objects.filter(trainer = trainer, client = client)
            if rating_object:
                rating_object = rating_object.get()
                rating_object.rating = int(rating)
            else:
                rating_object = Rating(rating=int(rating), trainer=trainer, client=client)
            rating_object.save()
        return redirect("/trainers/"+str(trainer_id))

@login_required
@user_passes_test(is_client)
def comment_trainer(request, trainer_id):
    if request.method == 'POST':
        client = Client.objects.filter(user = request.user)
        trainer = Trainer.objects.filter(id = trainer_id)
        comment = request.POST.get('comment', '')

        if not client or not trainer:
            messages.error(request, "El cliente o el entrenador no existen")

        if comment == '':
            messages.error(request, "No se ha escrito ningun comentario")
        else: 
            client = client.get()
            trainer = trainer.get()
            comment_object = Comment.objects.filter(trainer = trainer, client = client)
            if comment_object:
                comment_object = comment_object.get()
                comment_object.comment = comment
            else:
                comment_object = Comment(comment=comment, trainer=trainer, client=client)
            comment_object.save()
        return redirect("/trainers/"+str(trainer_id))
