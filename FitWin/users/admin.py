from django.contrib import admin
from .models import *

admin.site.register(Trainer)
admin.site.register(Client)
admin.site.register(Rating)
admin.site.register(Comment)