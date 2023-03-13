from django.conf import settings

from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialAccount, SocialToken

client_id = settings.GOOGLE_CLIENT_ID
client_secret = settings.GOOGLE_CLIENT_SECRET

def get_google_credentials(user):
    """
    Where user can be obtained with request.user
    For use when making requests for the Google API:
        from google.auth.transport.requests import AuthorizedSession
        
        authed_session = AuthorizedSession(credentials)
        response = authed_session.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/')
    """
    if (user.is_anonymous or not is_social_google(user)):
        return None

    account = SocialAccount.objects.get(user=user, provider="google")
    token = SocialToken.objects.get(
        account=account
    )

    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/calendar'],
    )

    return credentials

def is_social(user):
    return SocialAccount.objects.filter(user=user).exists()

def is_social_google(user):
    return SocialAccount.objects.filter(user=user, provider="google").exists()