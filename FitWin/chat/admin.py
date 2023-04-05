from django.contrib import admin
from .models import Channel, ChannelUser, ChannelMessage

# Register your models here.

class ChannelMessageInline(admin.TabularInline):
    model= ChannelMessage
    extra = 1

class ChannelUserInline(admin.TabularInline):
    model= ChannelUser
    extra = 1

class ChannelAdmin(admin.ModelAdmin):
    inlines = [ChannelMessageInline, ChannelUserInline]

    class Meta:
        model = Channel


admin.site.register(Channel, ChannelAdmin)
admin.site.register(ChannelUser)
admin.site.register(ChannelMessage)
