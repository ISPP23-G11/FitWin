from django.urls import path

from .import views

app_name="payments"

urlpatterns = [


        path('', views.home, name='home'),
        path('create-checkout-session/', views.create_checkout_session, name='checkout'),
        path('success/', views.success,name='success'),
        path('cancel/', views.cancel,name='cancel'),
]