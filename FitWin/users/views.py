from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User, Rating, Comment, is_client, is_trainer
from django.template import loader
from django.shortcuts import HttpResponse, redirect
from django.contrib import messages
from .forms import EditProfileForm, UserUpdateForm
from datetime import datetime


@login_required
@user_passes_test(is_trainer)
def handler_trainers(request):
    user = request.user
    trainer = User.objects.filter(user = user)
    if trainer:
        context = {}
        template = loader.get_template("main_trainers.html") 
        return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_client)
def handler_clients(request):
    user = request.user
    client = User.objects.filter(user = user)
    if client:
        context = {}
        template = loader.get_template("main_clients.html") 
        return HttpResponse(template.render(context, request))


@login_required
def EditTrainer(request):
    user = request.user.id
    trainer = User.objects.get(user__id=user)

    if request.method == 'POST':
        birthday = request.POST.get("birthday", "")
        errors=False
        
        u_form=UserUpdateForm(request.POST, instance=request.user)
        form = EditProfileForm(request.POST, request.FILES, instance=trainer)
       
        birthday = datetime.strptime(birthday, '%Y-%m-%d')

        if birthday >= datetime.now():
            errors=True
            messages.error(request, 'La fecha de cumpleaños tiene que ser anterior a hoy')

        if form.is_valid() and u_form.is_valid() and not errors:

            trainer.picture = form.cleaned_data.get('picture')
            trainer.birthday = form.cleaned_data.get('birthday')
            trainer.bio = form.cleaned_data.get('bio')

            trainer.save()
            u_form.save()

            return redirect('/trainers')
        
        else:
            messages.error(request, 'El perfil no se ha podido editar')

    else:
        u_form=UserUpdateForm(instance=request.user)
        form = EditProfileForm(instance=trainer)

    context = {
        'form':form,
        'u_form': u_form,
        
    }
    return render(request, 'editTrainer.html', context)


@login_required
def EditClient(request):
    user = request.user.id
    client = User.objects.get(user__id=user)

    if request.method == 'POST':

        birthday = request.POST.get("birthday", "")
        errors=False
        
        u_form=UserUpdateForm(request.POST, instance=request.user)
        form = EditProfileForm(request.POST, request.FILES, instance=client)

        birthday = datetime.strptime(birthday, '%Y-%m-%d')

        if birthday >= datetime.now():
            errors=True
            messages.error(request, 'La fecha de cumpleaños tiene que ser anterior a hoy')

        if form.is_valid() and u_form.is_valid() and not errors:

            client.picture = form.cleaned_data.get('picture')
            client.birthday = form.cleaned_data.get('birthday')
            client.bio = form.cleaned_data.get('bio')
            
          
            client.save()
            u_form.save()
            
            return redirect('/clients')
        else:
            messages.error(request, 'El perfil no se ha podido editar')

    else:
        u_form=UserUpdateForm(instance=request.user)
        form = EditProfileForm(instance=client)

    context = {
        'form':form,
        'u_form': u_form,
        
    }
    return render(request, 'editClient.html', context)

@login_required
def handler_trainer_details(request, trainer_id):
    context = {}
    trainer = User.objects.filter(id = trainer_id)
    user = User.objects.filter(user = request.user)
    context["template"] = "navbar.html"
    if trainer:
        trainer = trainer.get()
        context['trainer'] = trainer
        if user:
            user = user.get()
            context["client"] = True
            context["template"] = "navbar_clients.html"
            own_rating = Rating.objects.filter(trainer = trainer, client=user)
            own_comment = Comment.objects.filter(trainer = trainer, client = user)
            if own_rating:
                context["own_rating"] = own_rating.get().rating
            if own_comment:
                context['own_comment'] = own_comment.get()

        comments = Comment.objects.filter(trainer = trainer).order_by('date')
        context['comments'] = comments

        ratings = Rating.objects.filter(trainer = trainer)
        if ratings:
            sum = 0.0
            for r in ratings:
                sum += r.rating
            mean = sum / len(ratings)
            context['mean'] = mean

        else:
            mean = "No hay calificaciones para este entrenador"
    else:
        messages.error(request, "Entrenador no encontrado")
    
    template = loader.get_template("trainer_details.html") 
    return HttpResponse(template.render(context, request))

        
@login_required
def handler_client_details(request, client_id):
    context = {}
    client = User.objects.filter(id = client_id)
    user = User.objects.filter(user = request.user)
    context["template"] = "navbar.html"
    if user:
        context["template"] = "navbar_clients.html"
    if client:
        client = client.get()
        context['client'] = client
    else:
        messages.error(request, "No se ha encontrado al cliente")
    
    template = loader.get_template("client_details.html") 
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_client)
def rating_trainer(request, trainer_id):
    if request.method == 'POST':
        client = User.objects.filter(user = request.user)
        trainer = User.objects.filter(id = trainer_id)
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
        client = User.objects.filter(user = request.user)
        trainer = User.objects.filter(id = trainer_id)
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

