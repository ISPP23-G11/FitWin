from django.contrib import admin

from .models import *

admin.site.register(Announcement)
admin.site.register(Category)
admin.site.register(Calendar)

