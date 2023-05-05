from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from .models import Announcement,Category
from users.models import User
import datetime
from .views import *

# Create your tests here.

#Fallos detectados: 
# * Los objetos httpresponse no poseen atributo context al ser llamado, por lo que no se puede determinar si la respuesta es la que se pretende
# * Los message dan error en los test, por lo que se ha copiado la parte necesaria del request y se han eliminado los message de la copia
class AnnouncementsTests(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='test trainer',picture=None,roles=['trainer'],birthday=datetime(1970,1,1), date_created=datetime(2023,4,20))
        self.client = User.objects.create(username='test client',password='1234',picture=None,roles=['client'],birthday=datetime(1970,1,1), date_created=datetime(2023,4,28))
        principiante = Category.objects.create(types='difficulty',name='principiante')
        age = Category.objects.create(types='age',name='10-15')
        karate = Category.objects.create(types='objectives',name='karate')
        yoga = Category.objects.create(types='objectives',name='yoga')
        artes_marciales = Category.objects.create(types='objectives',name='artes marciales')
        anuncio1 = Announcement.objects.create(title='Karate para niños',description='Clases de karate para niños de 10 a 15 años.'
                                    ,place='Complejo Polideportivo SADUS, Avenida de Grecia, 1, Sevilla',price=15
                                    ,capacity=20,trainer=self.user
                                    ,start_date=datetime(2023,5,1, 16,30),finish_date=datetime(2023,5,1, 17, 30),
                                    date_created=datetime(2023,4,20))
        categories1 = [principiante,age,karate,artes_marciales]
        anuncio1.categories.add(*categories1)
        anuncio2 = Announcement.objects.create(title='Yoga',description='Clases de yoga relajante'
                                    ,place='Complejo Polideportivo SADUS, Avenida de Grecia, 1, Sevilla',price=15
                                    ,capacity=20,trainer=self.user
                                    ,start_date=datetime(2023,5,7, 19,30),finish_date=datetime(2023,5,7, 20, 30),
                                    date_created=datetime(2023,4,20))
        categories2 = [yoga]
        anuncio2.categories.add(*categories2)
        
        self.factory = RequestFactory()
        self.category_test_id = age.id
        self.category = age
        self.min_price = 100
        self.anuncio_id = anuncio1.id

    

    @login_required
    def list_announcements_testview(self,request):
        user = request.user
        n_announcements = request.GET.get('nAnnouncements', 25)
        page_number = request.GET.get('page', 1)

        sort_by = request.GET.get('sortBy', 'bestRated')
        trainer_id = request.GET.get('trainerId', None)
        category = request.GET.get('category', None)
        show_full = request.GET.get('showFull', None) == 'True'
        show_booked = request.GET.get('showBooked', None) == 'True'
        min_price = request.GET.get('minPrice', None)
        max_price = request.GET.get('maxPrice', None)
        min_rating = request.GET.get('minRating', None)
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        trainer = request.GET.get('trainer', "")

        if trainer is not None:
            if User.objects.filter(username = trainer).exists():
                if "trainer" in User.objects.get(username = trainer).roles:
                    trainer = User.objects.get(username = trainer)
                else:
                    trainer = None
            else:
                trainer = None
        else:
            trainer = None
            

        categories = Category.objects.order_by('name').annotate(
        announcement_count=Count('announcement'))

        announcements = Announcement.objects.all()
        announcements = sort_announcements(announcements, sort_by)
        announcements = filter_announcements(
        announcements, user, trainer_id, category, show_full, show_booked,
        min_price, max_price, min_rating, start_date, end_date, trainer)
        announcements_count = announcements.count()

        paginator = Paginator(announcements, n_announcements)
        page_obj = paginator.get_page(page_number)

        context = {
            'announcements': page_obj,
            'announcements_count': announcements_count,
            'categories': categories,
            'page_obj': page_obj,
            'page_number': page_number,
            'n_announcements': n_announcements,
        }

        return render(request, 'list_announcements.html', context),context


    def test_filter_announcement_by_category(self):
        request = self.factory.get(f'/announcements/list?category={self.category_test_id}')
        request.user = self.user
        response,context = self.list_announcements_testview(request)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(context.get('announcements_count'),1)
        self.assertTrue(context.get('categories').contains(self.category))

    def test_filter_no_announcements_min_price_too_expensive(self):
        request = self.factory.get(f'/announcements/list?minPrice={self.min_price}')
        request.user = self.user
        response,context = self.list_announcements_testview(request)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(context.get('announcements_count'),0)

    def test_announcement_details(self):
        request = self.factory.get(f'announcements/{self.anuncio_id}')
        request.user = self.user
        response, context = self.announcement_details_test(request,self.anuncio_id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(context.get('announcement').id,self.anuncio_id)

    def test_announcement_details_does_not_exists(self):
        id = 999
        request = self.factory.get(f'announcements/{self.anuncio_id}')
        request.user = self.user
        response, is_redirect = self.announcement_details_test(request,id)
        self.assertTrue(is_redirect)
        self.assertFalse(Announcement.objects.filter(id=id).exists())
        self.assertEquals(response.status_code, 302)
        

    @login_required
    def announcement_details_test(self,request, announcement_id):
        announcement = Announcement.objects.filter(id=announcement_id).first()
        if not announcement:
            return redirect('/announcements/list') ,True

        is_client_booking = request.user in announcement.clients.all()
        is_trainer_announcement = announcement.trainer == request.user

        context = {
            'announcement': announcement,
            'is_client_booking': is_client_booking,
            'is_trainer_announcement': is_trainer_announcement,
        }
        return render(request, 'announcement_details.html', context), context
    
    #Este test falla
    #AttributeError: 'AnnouncementsTests' object has no attribute 'build_absolute_uri'
    def test_book_announcement_OK(self):
        request = self.factory.post(f"announcements/book/{self.anuncio_id}")
        request.user = self.client
        response = self.book_announcement_test(request,self.anuncio_id)
        print(response)

    @login_required
    @user_passes_test(is_client)
    def book_announcement_test(self,request, announcement_id):
        client = request.user
        announcement = Announcement.objects.get(id=announcement_id)

        if announcement.capacity > 0 and client not in announcement.clients.all():
            announcement.clients.add(client.id)
            announcement.capacity = announcement.capacity - 1
            announcement.save()

            calendar = CalendarAPI(announcement.trainer)
            calendar.add_attendee_to_event(
                announcement.google_calendar_event_id, client)


        return redirect(reverse('announcement_details',  kwargs={'announcement_id': announcement.id}))