from django.test import TestCase
from users.models import User


class AuthTestCase(TestCase):
    def setUp(self):
        trainer = User(
            username='trainer1',
            first_name='John',
            last_name='Doe',
            email='johndoe@ex.com',
            bio='A sample, sort of short text. Maybe not so short. Just slighly.',
            birthday='2001-01-01',
            roles=['trainer']
        )
        trainer.set_password('123')
        trainer.save()

        client = User(
            username='client1',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@ex.com',
            bio='A sample, sort of long text. Quite long. Very.',
            birthday='2001-12-31',
            roles=['client']
        )
        client.set_password('123')
        client.save()

        admin = User(username='admin')
        admin.set_password('admin')
        admin.is_superuser = True
        admin.save()

    def tearDown(self):
        self.client = None

    def test_login_trainer(self):
        data = {'username': 'trainer1', 'password': '123'}
        response = self.client.post(
            '/login', data, format='json', follow=True)

        self.assertRedirects(response, '/trainers')
        self.assertEqual(response.status_code, 200)

    def test_login_client(self):
        data = {'username': 'client1', 'password': '123'}
        response = self.client.post(
            '/login', data, format='json', follow=True)

        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

    def test_failed_login(self):
        data = {'username': 'trainer1', 'password': 'incorrect_password'}
        response = self.client.post(
            '/login', data, format='json', follow=True)

        self.assertRedirects(response, '/login')
        self.assertContains(
            response, 'El usuario y la contraseña son incorrectos')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        data = {'username': 'trainer1', 'password': '123'}
        response = self.client.post(
            '/login', data, format='json', follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/logout', format='json', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_register_trainer(self):
        data = {
            'username': 'trainer2',
            'email': 'nohjeod@ex.com',
            'password': '123',
            'password_again': '123',
            'bio': '.ylhgils tsuJ .trohs os ton ebyaM .txet trohs fo tros ,elpmas A',
            'birthday': '1002-10-10',
            'name': 'Nhoj',
            'last_name': 'Eod',
        }
        response = self.client.post(
            '/register/trainer/', data, format='json', follow=True)
        self.assertRedirects(response, '/login')
        self.assertEqual(response.status_code, 200)

        data = {'username': 'trainer2', 'password': '123'}
        response = self.client.post(
            '/login', data, format='json', follow=True)

        self.assertRedirects(response, '/trainers')
        self.assertEqual(response.status_code, 200)

    def test_register_client(self):
        data = {
            'username': 'client2',
            'email': 'enajeod@ex.com',
            'password': '123',
            'password_again': '123',
            'bio': '.yreV .gnol etiuQ .txet gnol fo tros ,elpmas A',
            'birthday': '1002-10-10',
            'name': 'Nhoj',
            'last_name': 'Eod',
        }
        response = self.client.post(
            '/register/client/', data, format='json', follow=True)
        self.assertRedirects(response, '/login')
        self.assertEqual(response.status_code, 200)

        data = {'username': 'client2', 'password': '123'}
        response = self.client.post(
            '/login', data, format='json', follow=True)

        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)
