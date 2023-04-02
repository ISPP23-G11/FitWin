from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views



urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('login', views.login, name='login'),
    path('logout', LogoutView.as_view()),
    path('register/<str:role>/', views.register, name='register'),
]