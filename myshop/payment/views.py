import braintree
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order

#egzemplarz bramki platnosci Braintree

gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        #pobieranie tokena nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # utworznie i przesłanie transakcji
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # oznaczenie zamowienia jako oplacone
            order.paid = True
            # Zapisanie unikatowego identyfikatora transakcji
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # wygenerowanie tokena
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})
