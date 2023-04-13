from django.http import HttpResponse
from django.template import loader


def home(request):
    template = loader.get_template('landingPage/home.html')

    return HttpResponse(template.render())

def principal(request):
    template = loader.get_template('principal.html')

def menu(request):
    template = loader.get_template('menu.html')
    return HttpResponse(template.render())