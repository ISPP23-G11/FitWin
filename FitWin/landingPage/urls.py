from django.urls import path
from . import views

urlpatterns = [
    path('landingPage/', views.home, name='home'),
    path('principal/', views.principal, name='principal'),
    path('menu/', views.menu, name='menu'),
]