from django.urls import path
from . import views

urlpatterns = [
    path('announcements/create', views.create_announcement, name='create'),
    path('', views.main, name='main'),
    path('login', views.login, name='login'),
    path('announcements/list-own/all', views.list_own_all, name='list_own_all'),
    path('announcements/add-categories/<int:announcement_id>', views.add_categories, name='add_categories'),
]