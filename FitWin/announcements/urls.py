from django.urls import path
from . import views

urlpatterns = [
    path('announcements/create', views.create_announcement, name='create'),
    path('announcements/edit/<int:announcement_id>', views.edit_announcement, name='edit'),
    path('announcements/list-own/all', views.list_own_all, name='list_own_all'),
    path('announcements/list-max-capacity-announ/all', views.list_max_capacity_announcements, name='list_max_capacity_announ'),
    path('announcements/add-categories/<int:announcement_id>', views.add_categories, name='add_categories'),
    path('announcements/delete-categories/<int:announcement_id>/<int:category_id>', views.delete_categories, name='delete_categories'),
    path('announcements/book/<int:announcement_id>', views.book_announcement, name='book_announcement'),
    path('announcements/cancelBook/<int:announcement_id>', views.cancel_book_announcement, name='cancel_book'),
    path('announcements/delete-announce/<int:announcement_id>', views.delete_announce, name='delete_announce'),
    path('announcements/list_client_announcements', views.list_client_announcements, name='list_client_announcements'),
    path('announcements/list-his/<int:trainer_id>', views.show_his_announcements),
    path('announcements/list-all', views.list_announcements, name='list_all'),
    path('announcements/<int:announcement_id>', views.handler_announcement_details, name='announcement_details'),
    path('plans/', views.plans, name='plans'),
]