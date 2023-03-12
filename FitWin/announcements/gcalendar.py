from authentication.credentials import get_google_credentials

from .models import Calendar
from allauth.socialaccount.models import EmailAddress

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarAPI():

    def __init__(self, user):
        self.user = user
        self.credentials = get_google_credentials(user)

    def create_calendar(self):
        created = None
        if self.user_is_authenticated() and not self.user_has_calendar():
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
        if self.user_is_authenticated() and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                calendar_id = Calendar.objects.filter(user=self.user) \
                                              .first().google_calendar_id
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

                event = service.events().insert(calendarId=calendar_id,
                                                body=event).execute()
                created = event['id']
        return created
    
    def edit_event(self,event_id,title,description,start_date,finish_date):
        edited = None
        if self.credentials is not None and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                calendar_id = Calendar.objects.filter(user=self.user) \
                                              .first().google_calendar_id
                try:
                    event = service.events().get(calendarId=calendar_id,
                                                 eventId=event_id).execute()
                    event['summary'] = title
                    event['description'] = description
                    event['start'] = {
                            'dateTime': start_date,
                            'timeZone': 'Europe/Madrid',
                        }
                    event['end'] = {
                            'dateTime': finish_date,
                            'timeZone': 'Europe/Madrid',
                        }

                    updated_event = service.events().update(calendarId=calendar_id,
                                                            eventId=event_id,
                                                            body=event).execute()
                    edited = updated_event['id']
                except HttpError:
                    pass
        return edited
    
    def delete_event(self, event_id):
        if self.credentials is not None and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                calendar_id = Calendar.objects.filter(user=self.user) \
                                              .first().google_calendar_id
                try:
                    service.events().delete(calendarId=calendar_id,
                                                      eventId=event_id).execute()
                except HttpError:
                    pass

    def add_attendee_to_event(self, event_id, user):
        edited = None
        if self.credentials is not None and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                email = EmailAddress.objects.filter(user=user).get().email
                calendar_id = Calendar.objects.filter(user=self.user) \
                                              .first().google_calendar_id
                try:
                    event = service.events().get(calendarId=calendar_id,
                                                 eventId=event_id).execute()

                    if 'attendees' in event:
                        event['attendees'] += [ {'email': email} ]
                    else:
                        event['attendees'] = [ {'email': email} ]

                    updated_event = service.events().update(calendarId=calendar_id,
                                                            eventId=event_id,
                                                            body=event).execute()
                    edited = updated_event['id']
                except HttpError:
                    pass
        return edited
    
    def remove_attendee_from_event(self, event_id, user):
        edited = None
        if self.credentials is not None and self.user_has_calendar():
            with build('calendar', 'v3', credentials=self.credentials) as service:
                email = EmailAddress.objects.filter(user=user).get().email
                calendar_id = Calendar.objects.filter(user=self.user) \
                                              .first().google_calendar_id
                try:
                    event = service.events().get(calendarId=calendar_id,
                                                 eventId=event_id).execute()
                    
                    if 'attendees' in event:
                        event['attendees'] = [
                            filter(lambda x: x['email'] != email,event['attendees'])
                        ]

                    updated_event = service.events().update(calendarId=calendar_id,
                                                             eventId=event_id,
                                                             body=event).execute()
                    edited = updated_event['id']
                except HttpError:
                    pass
        return edited

    def user_has_calendar(self):
        return Calendar.objects.filter(user=self.user).exists()
    
    def user_is_authenticated(self):
        return self.credentials is not None