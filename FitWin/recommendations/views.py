from django.shortcuts import render
from announcements.models import Announcement
from users.models import User, is_client
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Recommendation
# Create your views here.


@login_required
@user_passes_test(is_client)
def view_recommended(request):
    user = request.user.pk
    client = User.objects.filter(pk = user).get()
    recommendations = Recommendation.objects.filter(client=client).exclude(score__lt=3.5)
    announcements = Announcement.objects.filter(pk__in=recommendations.values_list('pk', flat=True)).distinct()
    return render(request, 'recommended.html', {'announcements': announcements})


