from authentication.credentials import get_google_credentials
from googleapiclient.discovery import build
from .models import Calendar
from allauth.socialaccount.models import EmailAddress


class CalendarAPI():

    def __init__(self, user):
        self.user = user
        self.credentials = get_google_credentials(user)

    def create_calendar(self):
        created = None
        if self.credentials is not None and not self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                calendar_request = {
                    'summary': 'Anuncios FitWin',
                    'timeZone': 'Europe/Madrid',
                }
                google_calendar = service.calendars().insert(body=calendar_request).execute()
                calendar = Calendar()
                calendar.google_calendar_id = google_calendar['id']
                calendar.user = self.user
                calendar.save()
            created = google_calendar['id']
        return created

    def create_event(self,title,description,start_date,finish_date):
        created = None
        if self.credentials is not None and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                calendar_id = Calendar.objects.filter(user=self.user).first().google_calendar_id
                email = EmailAddress.objects.filter(user=self.user).get().email

                event = {
                    'summary': title,
                    'description': description,
                    'start': {
                        'dateTime': start_date,
                        'timeZone': 'Europe/Madrid',
                    },
                    'end': {
                        'dateTime': finish_date,
                        'timeZone': 'Europe/Madrid',
                    },
                    'attendees': [
                        {'email': email},
                    ],
                    'reminders': {
                        'useDefault': True,
                    },
                }

                event = service.events().insert(calendarId=calendar_id, body=event).execute()
                created = event['id']
        return created


    def user_has_calendar(self):
        return Calendar.objects.filter(user=self.user).exists()