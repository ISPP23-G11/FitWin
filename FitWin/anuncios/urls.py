from django.urls import path
from . import views

urlpatterns = [
    path('announcements/create', views.create_announcement, name='create'),
    path('announcements/edit/<int:announcement_id>', views.edit_announcement, name='edit'),
    path('', views.main, name='main'),
    path('login', views.login, name='login'),
    path('announcements/list-own/all', views.list_own_all, name='list_own_all'),
    path('announcements/add-categories/<int:announcement_id>', views.add_categories, name='add_categories'),
    path('announcements/delete-categories/<int:announcement_id>/<int:category_id>', views.delete_categories, name='delete_categories'),
]