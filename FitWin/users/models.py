from allauth.account.utils import get_next_redirect_url
from allauth.socialaccount.models import SocialLogin
from allauth.utils import get_request_param
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
    num_announcements = models.PositiveIntegerField(default=0)

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

@classmethod
def state_from_request(cls, request):
    ''''
    Override all-auth SocialLogin.state_from_request to include role parameter.
    '''
    state = {}
    next_url = get_next_redirect_url(request)

    try:
        request.session["role"] = get_request_param(request, "role", None)
    except KeyError:
        print('user_type not exist')

    if next_url:
        state["next"] = next_url
    state["process"] = get_request_param(request, "process", "login")
    state["scope"] = get_request_param(request, "scope", "")
    state["auth_params"] = get_request_param(request, "auth_params", "")

    return state

SocialLogin.state_from_request = state_from_request