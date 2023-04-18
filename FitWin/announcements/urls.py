from django.urls import path

from . import views

urlpatterns = [
    path('announcements/create', views.create_announcement,
         name='create_announcement'),
    path('announcements/edit/<int:announcement_id>',
         views.edit_announcement, name='edit_announcement'),
    path('announcements/delete/<int:announcement_id>',
         views.delete_announcement, name='delete_announcement'),
    path('announcements/<int:announcement_id>',
         views.announcement_details, name='announcement_details'),

    path('announcements/add-categories/<int:announcement_id>',
         views.add_categories, name='add_categories'),
    path('announcements/delete-categories/<int:announcement_id>/<int:category_id>',
         views.delete_categories, name='delete_categories'),
    path('announcements/book/<int:announcement_id>',
         views.book_announcement, name='book_announcement'),
    path('announcements/cancelBook/<int:announcement_id>',
         views.cancel_book_announcement, name='cancel_book'),

    path('announcements/list', views.list_announcements, name='list_announcements'),
]
