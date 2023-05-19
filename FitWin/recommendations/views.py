from django.shortcuts import render
from announcements.models import Announcement
from users.models import User, is_client
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Recommendation , create_similarities
# Create your views here.


@login_required
@user_passes_test(is_client)
def view_recommended(request):
    user = request.user.pk
    client = User.objects.filter(pk = user).get()
    create_similarities(client)
    announcements = Announcement.objects.filter(recommendation__client=client, recommendation__score__gte=3.5).distinct()
    return render(request, 'recommended.html', {'announcements': announcements})


