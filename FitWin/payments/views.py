from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from django.utils.html import strip_tags
from django.http import JsonResponse

# Create your views here.

def home(request):

    url = '/payments/create-checkout-session/'
    context = {'url':url}
    return render(request,'payments/payment.html', context=context)


def cancel(request):
    return render(request,'payments/cancel.html')

def success(request):
    return render(request,'payments/success.html')

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = settings.BASEURL

@csrf_exempt
def create_checkout_session(request):
    print("Entra en checkout")
   
    total = 4.99
   
      
    total_formated = str("%.2f" % total).replace('.','')
    
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