from django.urls import path
from . import views

urlpatterns = [
    path('trainers', views.handler_trainers, name='main'),
    path('clients', views.handler_clients, name='main'),
    path('trainer/edit', views.EditTrainer, name="edit-trainer"),
    path('client/edit', views.EditClient, name="edit-client"),
    path('clients/rating/<int:trainer_id>', views.rating_trainer),
    #URL de la vista detalle del entrenador donde hay un formulario para votar con la URL de arriba
    # path('trainers/<int:trainer_id>', views.trainers_detail),
    path('clients/comment/<int:trainer_id>', views.comment_trainer),
 

]
