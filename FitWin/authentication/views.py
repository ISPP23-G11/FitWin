import re
from datetime import datetime

from allauth.account.signals import user_signed_up
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.dispatch import receiver
from django.shortcuts import HttpResponse, redirect
from django.template import loader
from django.urls import reverse
from users.models import User, is_client, is_trainer


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_django(request, user)
            if is_trainer(user):
                return redirect('/trainers')
            elif is_client(user):
                return redirect('/clients')
            else:
                return redirect(reverse('home'))
        else:
            messages.error(request, 'El usuario y la contraseña son incorrectos')
            return redirect('/login')
    else:
        template = loader.get_template('account/login.html')
        context = {}
        return HttpResponse(template.render(context, request))


def register(request, role):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_again = request.POST.get('password_again', '')
        bio = request.POST.get('bio', '')
        birthday = request.POST.get('birthday', '')
        picture = request.FILES['picture']
        name = request.POST.get('name', '')
        last_name = request.POST.get('last_name', '')
        if validate_role(role):
            roles = [role]

        errors = validate_register_form(request, username, email, password, password_again,
                                        bio, birthday, picture, name, last_name, roles)

        if not errors:
            user = User.objects.create_user(username = username, password=password,
                                            email=email, first_name=name, last_name=last_name,
                                            bio=bio, birthday=birthday, roles=roles)
            user.picture.save(picture.name, picture)
            user.save()
            return redirect('/login')
        else:
            return redirect('/register/'+role)
    else:
        template = loader.get_template('account/register.html')
        context = {
            'role': role,
        }
        return HttpResponse(template.render(context, request))

def validate_register_form(request, username, email, password, password_again, bio, birthday,
                           picture, name, last_name, roles):
    old_user = User.objects.filter(username = username)

    errors = False
    if old_user:
        errors = True
        messages.error(request, 'Este nombre de usuario ya existe')

    if password != password_again:
        errors = True
        messages.error(request, 'Las contraseñas no coinciden')

    if birthday!= '':
        birthday = datetime.strptime(birthday, '%Y-%m-%d')
        if birthday >= datetime.now():
            errors = True
            messages.error(request, 'La fecha de nacimiento debe ser anterior a hoy')
    else:
        errors = True
        messages.error(request, 'La fecha de naciemiento es obligatoria')

    email_val = re.fullmatch('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)
    if not email_val:
        errors = True
        messages.error(request, 'El email no sigue un formato valido. Por ejemplo: prueba@host.com')

    return errors


@receiver(user_signed_up)
def assign_role_to_user(sender, request, user, **kwargs):
    '''
    Assign role to user after social (google) sign-up
    '''
    role = request.session['role']
    if validate_role(role):
        user.roles = [role]
    user.save()

def validate_role(role):
    return role in ['client', 'trainer']