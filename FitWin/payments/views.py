from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from django.utils.html import strip_tags
from django.http import JsonResponse
from users.views import upgrade_suscription, is_premium
from users.models import User
from django.contrib import messages


# Create your views here.

def cancel(request):
    return render(request,'payments/cancel.html')

def success(request):
    trainer = request.user
    #trainer = User.objects.get(user = user)
    upgrade_suscription(trainer)
    return render(request,'payments/success.html')

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = settings.BASEURL

@csrf_exempt
def create_checkout_session(request):
    print("Entra en checkout")
   
    total = 4.99
     
    total_formated = str("%.2f" % total).replace('.','')

    trainer = request.user
    #trainer = Trainer.objects.get(user = user)

    if not is_premium(trainer):

        session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': 'Pago en Fitwin',
                },
                'unit_amount': total_formated,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/payments/success',
        cancel_url=YOUR_DOMAIN + '/payments/cancel',
        )
        

        return JsonResponse({'id': session.id})
    
    else:
        messages.error(request, "Ya eres entrenador premium")
        return redirect('/trainers')


def plans(request):
    user = request.user
    trainer = Trainer.objects.filter(user = user)
    url = '/payments/create-checkout-session/'
    trainer=trainer.get()

    context = {'url':url, 'trainer':trainer}
    template = loader.get_template('payments/plans.html')
    return HttpResponse(template.render(context, request))