import json
import requests

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between
)


HOST = 'http://localhost:8000'


class DefTrainers(SequentialTaskSet):

    def on_start(self):
        with open('trainers.json') as f:
            self.users = json.loads(f.read())
        self.user_ = choice(list(self.users))

    @task
    def login(self):
        url = f'{HOST}/login'

        username, pwd = self.user_['username'], self.user_['password']
        data = {
            'username': username,
            'password': pwd,
        }

        csrf_token = requests.get(url).cookies['csrftoken']
        headers = {'X-CSRFToken': csrf_token}
        cookies = {"csrftoken": csrf_token}
        data['csrfmiddlewaretoken'] = csrf_token

        response = self.client.post(
            '/login', data, headers=headers, cookies=cookies)

    @task
    def create_announcement(self):
        url = f'{HOST}/announcements/create'
        data = {
            'title': 'Announcement Title',
            'description': 'A very detailed description',
            'place': 'Av. Test n42 2A, 1092 Test, Test',
            'price': '42.42',
            'capacity': '42',
            'day': '2024-01-01',
            'start_date': '10:20',
            'finish_date': '12:50',
        }

        csrf_token = requests.get(url).cookies['csrftoken']
        headers = {'X-CSRFToken': csrf_token}
        cookies = {"csrftoken": csrf_token}
        data['csrfmiddlewaretoken'] = csrf_token

        response = self.client.post(
            '/announcements/create', data, headers=headers, cookies=cookies)

    def on_quit(self):
        self.user_ = None


class DefClients(SequentialTaskSet):

    def on_start(self):
        with open('clients.json') as f:
            self.users = json.loads(f.read())
        self.user_ = choice(list(self.users))

        self.booked = False
        with open('created_announcements.json') as f:
            self.announcements = json.loads(f.read())
        self.announcement = choice(list(self.announcements))

    @task
    def login(self):
        url = f'{HOST}/login'

        username, pwd = self.user_['username'], self.user_['password']
        data = {
            'username': username,
            'password': pwd,

        }

        csrf_token = requests.get(url).cookies['csrftoken']
        headers = {"X-CSRFToken": csrf_token}
        cookies = {"csrftoken": csrf_token}
        data['csrfmiddlewaretoken'] = csrf_token

        response = self.client.post(
            '/login', data, headers=headers, cookies=cookies)

    @task
    def book_announcement(self):

        if self.booked:
            url = f'{HOST}/announcements/book/{self.announcement}'
            csrf_token = requests.get(url).cookies['csrftoken']
            headers = {"X-CSRFToken": csrf_token}
            cookies = {"csrftoken": csrf_token}

            response = self.client.post(
                f'/announcements/cancelBook/{self.announcement}', headers=headers, cookies=cookies, name='/announcements/cancelBook')
            if (response.status_code == 200):
                self.booked = False
        else:
            url = f'{HOST}/announcements/cancelBook/{self.announcement}'
            csrf_token = requests.get(url).cookies['csrftoken']
            headers = {"X-CSRFToken": csrf_token}
            cookies = {"csrftoken": csrf_token}

            response = self.client.post(
                f'/announcements/book/{self.announcement}', headers=headers, cookies=cookies, name='/announcements/book')
            if (response.status_code == 200):
                self.booked = True

    @task
    def list_announcements(self):
        url = f'{HOST}/announcements/list'
        csrf_token = requests.get(url).cookies['csrftoken']
        headers = {"X-CSRFToken": csrf_token}
        cookies = {"csrftoken": csrf_token}

        response = self.client.get(
            f'/announcements/list', headers=headers, cookies=cookies, name='/announcements/list')

    def on_quit(self):
        self.user_ = None


class Trainers(HttpUser):
    host = HOST
    tasks = [DefTrainers]
    wait_time = between(3, 5)


class Clients(HttpUser):
    host = HOST
    tasks = [DefClients]
    wait_time = between(3, 5)
