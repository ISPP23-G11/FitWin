from django.db import models
from django.contrib.postgres.fields import ArrayField

import os

from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.validators import MaxValueValidator, MinValueValidator


def user_directory_path(instance, filename):
	return 'users/{0}'.format(filename)

class User(AbstractUser):
    picture=models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    birthday=models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=15, null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    date_premium = models.DateField(null=True, blank=True)
    roles = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True
    )


class Rating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rating_trainer")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rating_client")

class Comment(models.Model):
    comment = models.TextField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_trainer")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_client")
    date = models.DateTimeField(auto_now=True)

def is_trainer(user):
    if User.objects.filter(id = user.id).exists():
        if User.objects.get(id = user.id).roles is not None:
            return "trainer" in User.objects.get(id = user.id).roles
    return False

def is_client(user):
    if User.objects.filter(id = user.id).exists():
        if User.objects.get(id = user.id).roles is not None:
            return "client" in User.objects.get(id = user.id).roles
    return False

# class Trainer(models.Model): 
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     picture=models.ImageField(upload_to=user_directory_path, blank=True, null=True)
#     date_created = models.DateField(auto_now_add=True)
#     birthday=models.DateField(null=True, blank=True)
#     bio = models.TextField(max_length=150, null=True, blank=True)

# class Client(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     picture=models.ImageField(upload_to=user_directory_path, blank=True, null=True)
#     date_created = models.DateField(auto_now_add=True)
#     birthday=models.DateField(null=True, blank=True)
#     bio = models.TextField(max_length=150, null=True, blank=True)

# class Rating(models.Model):
#     rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
#     trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)

# class Comment(models.Model):
#     comment = models.TextField()
#     trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now=True)

