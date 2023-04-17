from django.urls import path

from . import views

urlpatterns = [
    path('trainers', views.handler_trainers, name='main_trainers'),
    path('clients', views.handler_clients, name='main_clients'),
    path('trainers/<int:trainer_id>',
         views.handler_trainer_details, name='trainer_details'),

    path('trainer/edit', views.EditTrainer, name="trainer_edit"),
    path('client/edit', views.EditClient, name="client_edit"),

    path('clients/<int:client_id>',
         views.handler_client_details, name='client_details'),

    path('clients/rating/<int:trainer_id>', views.rating_trainer),
    # URL de la vista detalle del entrenador donde hay un formulario para votar con la URL de arriba
    path('clients/comment/<int:trainer_id>', views.comment_trainer),


]
