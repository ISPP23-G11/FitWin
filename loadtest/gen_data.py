import requests
import random
import string
import json


HOST = "http://localhost:8000"


class User:
    def __init__(self, username, password, password_again, name, last_name, email, bio, birthday, roles):
        self.username = username
        self.password = password
        self.password_again = password_again
        self.name = name
        self.last_name = last_name
        self.email = email
        self.bio = bio
        self.birthday = birthday
        self.roles = roles
        # self.is_premium = is_premium


def generate_username():
    return ''.join(random.choices(string.ascii_lowercase, k=8))


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def generate_email():
    domain = random.choice(['ex.com', 'example.com', 'test.com'])
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{username}@{domain}"


def generate_bio(length):
    text = ''.join(random.choices(string.ascii_letters +
                   string.digits + string.punctuation + ' ', k=length))
    return text.strip()


def generate_birthday():
    year = random.randint(1950, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate_test_users(role, n):
    users = []
    for i in range(n):
        username = generate_username()
        password = generate_password()
        password_again = password
        name = random.choice(['John', 'Jane', 'Mike', 'Emily'])
        last_name = random.choice(['Doe', 'Smith', 'Johnson', 'Brown'])
        email = generate_email()
        bio = generate_bio(50) if role == 'trainer' else generate_bio(100)
        birthday = generate_birthday()
        roles = [role]
        # is_premium = random.choice([True, False])
        user = User(username, password, password_again, name, last_name,
                    email, bio, birthday, roles)
        users.append(user)
    return users


def save_users_to_json(users, file):
    data = []
    for user in users:
        data.append(user.__dict__)
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def create_users(filename):

    with open(filename) as f:
        users = json.loads(f.read())

    valid_users = []
    invalid_users = []
    announcements = []
    for user in users:
        url = f"{HOST}/register/{user['roles'][0]}/"

        csrf_token = requests.get(url).cookies['csrftoken']
        headers = {"X-CSRFToken": csrf_token}
        cookies = {"csrftoken": csrf_token}
        user['csrfmiddlewaretoken'] = csrf_token

        response = requests.post(
            url, data=user, headers=headers, cookies=cookies)

        if response.status_code == 200:
            valid_users.append(user['username'])
        else:
            invalid_users.append(user['username'])

        if (random.choice([True, False]) and 'trainer' in user['roles']):
            response = create_announcement(user)
            id = response.url.split('/')[-1]
            announcements.append(id)

        with open('created_announcements.json', 'w') as f:
            json.dump(announcements, f, indent=4)

    return valid_users, invalid_users


def login(user, session):
    url = f'{HOST}/login'

    username, pwd = user['username'], user['password']
    data = {
        'username': username,
        'password': pwd,
    }

    csrf_token = requests.get(url).cookies['csrftoken']
    headers = {'X-CSRFToken': csrf_token}
    cookies = {"csrftoken": csrf_token}
    data['csrfmiddlewaretoken'] = csrf_token

    response = session.post(
        url, data, headers=headers, cookies=cookies)

    return response


def create_announcement(user):
    session = requests.Session()
    login(user, session)

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

    response = session.post(
        url, data, headers=headers, cookies=cookies)

    return response


trainers = generate_test_users('trainer', 20)
save_users_to_json(trainers, 'trainers.json')
clients = generate_test_users('client', 20)
save_users_to_json(clients, 'clients.json')

valid_users, invalid_users = create_users('clients.json')
print(valid_users, invalid_users)
valid_users, invalid_users = create_users('trainers.json')
print(valid_users, invalid_users)
