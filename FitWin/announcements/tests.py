from urllib import response
from django.test import TestCase
from django.urls import reverse
from .models import Announcement, Category
from users.models import User
import datetime
from .views import *

# Create your tests here.

# Fallos detectados:
# * Los objetos httpresponse no poseen atributo context al ser llamado, por lo que no se puede determinar si la respuesta es la que se pretende
# * Los message dan error en los test, por lo que se ha copiado la parte necesaria del request y se han eliminado los message de la copia


class AnnouncementsTests(TestCase):

    def setUp(self) -> None:
        trainer = User(
            username='trainer',
            picture=None,
            roles=['trainer'],
            birthday=datetime(1970, 1, 1),
            date_created=datetime(2023, 4, 20)
        )
        trainer.set_password('1234')
        trainer.save()
        self.trainer = trainer

        client_ = User(
            username='client',
            picture=None,
            roles=['client'],
            birthday=datetime(1970, 1, 1),
            date_created=datetime(2023, 4, 28)
        )
        client_.set_password('1234')
        client_.save()
        self.client_ = client_

        principiante = Category.objects.create(
            types='difficulty', name='principiante')
        age = Category.objects.create(types='age', name='10-15')
        karate = Category.objects.create(types='objectives', name='karate')
        yoga = Category.objects.create(types='objectives', name='yoga')
        artes_marciales = Category.objects.create(
            types='objectives', name='artes marciales')
        anuncio1 = Announcement.objects.create(
            title='Karate para niños',
            description='Clases de karate para niños de 10 a 15 años.',
            place='Complejo Polideportivo SADUS, Avenida de Grecia, 1, Sevilla',
            price=15,
            capacity=20,
            trainer=self.trainer,
            start_date=datetime(2023, 5, 1, 16, 30),
            finish_date=datetime(2023, 5, 1, 17, 30),
            date_created=datetime(2023, 4, 20)
        )
        categories1 = [principiante, age, karate, artes_marciales]
        anuncio1.categories.add(*categories1)
        anuncio2 = Announcement.objects.create(
            title='Yoga',
            description='Clases de yoga relajante',
            place='Complejo Polideportivo SADUS, Avenida de Grecia, 1, Sevilla',
            price=15,
            capacity=20,
            trainer=self.trainer,
            start_date=datetime(2023, 5, 7, 19, 30),
            finish_date=datetime(2023, 5, 7, 20, 30),
            date_created=datetime(2023, 4, 20)
        )
        categories2 = [yoga]
        anuncio2.categories.add(*categories2)

        self.category_test_id = age.id
        self.category = age
        self.min_price = 100
        self.anuncio_id = anuncio1.id

    def test_filter_announcement_by_category(self):
        response = self.client.post(
            '/login', {'username': 'client', 'password': '1234'}, format='json', follow=True)
        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/announcements/list?category={self.category_test_id}')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['announcements_count'], 1)
        self.assertTrue(response.context['categories'].contains(self.category))

    def test_filter_no_announcements_min_price_too_expensive(self):
        response = self.client.post(
            '/login', {'username': 'client', 'password': '1234'}, format='json', follow=True)
        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/announcements/list?minPrice={self.min_price}')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['announcements_count'], 0)

    def test_announcement_details(self):
        response = self.client.post(
            '/login', {'username': 'client', 'password': '1234'}, format='json', follow=True)
        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/announcements/{self.anuncio_id}')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['announcement'].id, self.anuncio_id)

    def test_announcement_details_does_not_exists(self):
        response = self.client.post(
            '/login', {'username': 'client', 'password': '1234'}, format='json', follow=True)
        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

        id = 999
        response = self.client.get(f'/announcements/{id}')
        self.assertFalse(Announcement.objects.filter(id=id).exists())
        self.assertEquals(response.status_code, 302)

    def test_book_announcement_OK(self):
        response = self.client.post(
            '/login', {'username': 'client', 'password': '1234'}, format='json', follow=True)
        self.assertRedirects(response, '/clients')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            f"/announcements/book/{self.anuncio_id}", follow=True)
        self.assertEqual(response.status_code, 200)
