from django.urls import path
from . import views

urlpatterns = [
    path('trainers', views.handler_trainers, name='main'),
    path('clients', views.handler_clients, name='main'),
    path('trainers/<int:trainer_id>', views.handler_trainer_details, name='main'),


]