from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
	return 'users/{0}'.format(filename)

class Trainer(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture=models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)
