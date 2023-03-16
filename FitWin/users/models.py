from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Trainer(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)
    

