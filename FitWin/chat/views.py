from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, View
from django.views.generic.edit import FormMixin

from .forms import FormMessages
from .models import Channel, ChannelMessage


class Inbox(View):
    def get(self, request):

        inbox = Channel.objects.filter(channeluser__user__in=[request.user.id])

        context = {
            "inbox":inbox
        }
        return render(request, 'chat/inbox.html', context)

class ChannelFormMixin(FormMixin):
    form_class=FormMessages
   # succes_url = "./"

    def get_succes_url(self):
        return self.request.path


    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied

        form = self.get_form()
        if form.is_valid():
            channel = self.get_object()
            user = self.request.user
            message = form.cleaned_data.get("message")
            channel_obj= ChannelMessage.objects.create(channel=channel, user=user, text=message)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'message':channel_obj.text,
                    'username':channel_obj.user.username
                    }, status=201)
            return super().form_valid(form)
        
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"Error":form.errors}, status=400)

            return super().form_invalid(form)


class ChannelDetailView(LoginRequiredMixin, ChannelFormMixin, DetailView):

    template_name='chat/channel_detail.html'
    queryset=Channel.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        obj = context['object']
        print(obj)
        

        """ if self.request.user not in obj.users.all():
            raise PermissionDenied """

        context['si_canal_miembro']=self.request.user in obj.users.all()

        return context

    """ def get_queryset(self):

        usuario = self.request.user
        username=usuario.username
        qs = Channel.objects.all().filter_by_username(username)
        return qs """


class DetailMs(LoginRequiredMixin, ChannelFormMixin, DetailView):

    template_name='chat/channel_detail.html'

    def get_object(self, *args, **kwargs):

        username=self.kwargs.get("username")
        my_username = self.request.user.username
        channel, _ = Channel.objects.get_or_create_channel_ms(my_username, username)

        if username == my_username:
            my_channel, _ = Channel.objects.get_or_create_channel_current_user(self.request.user)
            return my_channel

        if channel==None:
            return Http404
            
        return channel



def private_messages(request, username, *args, **kwargs):

    if not request.user.is_authenticated:
        return HttpResponse("Prohibido")

    my_username = request.user.username

    channel, created = Channel.objects.get_or_create_channel_ms(my_username,username)

    if created:
        print("Si, fue creado")
    
    return HttpResponse(f"Nuestro Id del Canal - {channel.id}")