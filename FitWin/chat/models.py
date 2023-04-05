from django.db import models
import uuid
from django.conf import settings
from django.db.models import Count
from django.apps import apps
from django.contrib.auth.models import User

# Create your models here.

class ModelBase(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True, editable=False)
    time = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta: 
        abstract = True


class ChannelMessage(ModelBase):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

class ChannelUser(ModelBase):
    channel = models.ForeignKey("Channel", null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ChannelQuerySet(models.QuerySet):

    def only_one(self):
        return self.annotate(num_users=Count("users")).filter(num_users=1)

    def only_two(self):
        return self.annotate(num_users=Count("users")).filter(num_users=2)

    def filter_by_username(self, username):
        return self.filter(channeluser__user__username=username)

class ChannelManager(models.Manager):
    
    def get_queryset(self, *args, **kwargs):
        return ChannelQuerySet(self.model, using=self.db)

    def filter_ms_by_pivate(self, username_a, username_b):
        return self.get_queryset().only_two().filter_by_username(username_a).filter_by_username(username_b)

    def get_or_create_channel_current_user(self, user):
        qs = self.get_queryset().only_one().filter_by_username(user.username)

        if qs.exists():
            return qs.order_by("time").first, False

        channel_obj=Channel.objects.create()
        ChannelUser.objects.create(user=user, channel=channel_obj)

        return channel_obj, True

    def get_or_create_channel_ms(self, username_a, username_b):
        qs = self.filter_ms_by_pivate(username_a, username_b)

        if qs.exists():

            return qs.order_by("time").first(), False

        #User = apps.get_model("auth", model_name='User')
        user_a, user_b = None, None

        try:
            user_a=User.objects.get(username=username_a)

        except User.DoesNotExist:
            return None, False

        try:
            user_b=User.objects.get(username=username_b)

        except User.DoesNotExist:
            return None, False

        if user_a == None or user_b == None:
            return None, False

        obj_channel = Channel.objects.create()

        channel_user_a=ChannelUser(user=User.objects.get(username=username_a), channel=obj_channel)
        channel_user_b=ChannelUser(user=User.objects.get(username=username_b), channel=obj_channel)
        ChannelUser.objects.bulk_create([channel_user_a, channel_user_b])
        return obj_channel, True


class Channel(ModelBase):
    users = models.ManyToManyField(User, blank=True, through=ChannelUser)

    objects = ChannelManager()