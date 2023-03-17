from django.urls import path
from . import views

urlpatterns = [
    path('trainers', views.handler_trainers, name='main'),
    path('clients', views.handler_clients, name='main'),
    path('trainer/edit', views.EditTrainer, name="edit-trainer"),
    path('client/edit', views.EditClient, name="edit-client"),

]