from django.test import TestCase
from users.models import User, Comment
from django.urls import reverse
# Create your tests here.

class UsersTestCase(TestCase):
    def setUp(self):
        trainer = User(
            username='entrenador1',
            first_name='Juan',
            last_name='Perez',
            email='ejemplo@gmail.com',
            bio='Ejemplo de bio',
            birthday='1990-01-01',
            roles=['trainer']
        )
        trainer.set_password('123')
        trainer.save()

        client = User(
            username='cliente1',
            first_name='Pablo',
            last_name='Dominguez',
            email='ejemplo2@gmail.com',
            bio='Ejemplo de bio de cliente',
            birthday='1999-01-01',
            roles=['client']
        )
        client.set_password('123')
        client.save()


    def tearDown(self):
        
        self.client = None
        self.trainer = None
        

    
    def test_edit_profile_trainer(self):

        self.client.login(username='entrenador1', password='123')
        response = self.client.post('/trainer/edit', {
                'first_name': 'Juan Pedro',
                'last_name': 'Perez Martinez',
                'bio': 'Ejemplo de bio actualizado',
                'birthday': '1990-01-01',
            })
        
        self.assertEqual(response.status_code, 302)

        trainer = User.objects.get(username='entrenador1')

        self.assertEqual(trainer.first_name, 'Juan Pedro')
        self.assertEqual(trainer.last_name, 'Perez Martinez')
        self.assertEqual(trainer.bio, 'Ejemplo de bio actualizado')

    def test_edit_profile_client(self):
        
        self.client.login(username='cliente1', password='123')
        
        response = self.client.post('/client/edit', {
            'first_name': 'Pablo Jesus',
            'last_name': 'Dominguez Ortiz',
            'bio': 'Ejemplo de bio actualizado',
            'birthday': '1999-01-01',
        })
        
        self.assertEqual(response.status_code, 302)

        client = User.objects.get(username='cliente1')

        self.assertEqual(client.first_name, 'Pablo Jesus')
        self.assertEqual(client.last_name, 'Dominguez Ortiz')
        self.assertEqual(client.bio, 'Ejemplo de bio actualizado')

    def test_edit_profile_trainer_failed(self):
        self.client.login(username='entrenador1', password='123')

        response = self.client.post('/trainer/edit', {
            'first_name': 'Juan Pedro',
            'last_name': 'Perez Martinez',
            'bio': 'Ejemplo de bio actualizado',
            'birthday': '2030-02-01',  # Formato incorrecto
        })
        self.assertEqual(response.status_code, 200)
        trainer = User.objects.get(username='entrenador1')

        self.assertNotEqual(trainer.birthday, '2030-02-01')

    def test_edit_profile_client_failed(self):
        self.client.login(username='cliente1', password='123')

        response = self.client.post('/client/edit', {
            'first_name': 'Pablo Jesus',
            'last_name': 'Dominguez Ortiz',
            'bio': 'Ejemplo de bio actualizado',
            'birthday': '2030-02-01',  # Fecha inválida
        })
        
        self.assertEqual(response.status_code, 200)

        client = User.objects.get(username='cliente1')

        self.assertNotEqual(client.birthday, '2030-02-01')

        

    