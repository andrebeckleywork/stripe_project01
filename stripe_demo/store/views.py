import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Order

stripe.api_key = settings.STRIPE_SECRET_KEY



# ------------------------------------------------------------------
# 1. Storefront — reads all available products from the database
# ------------------------------------------------------------------
def product_list(request):
    products = Product.objects.filter(available=True)
    return render(request, 'store/product_list.html', {
        'products': products,
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


# ------------------------------------------------------------------
# 2. Create Checkout Session — driven by the product's database record
# ------------------------------------------------------------------
def create_checkout_session(request, product_id):
    if request.method != 'POST':
        return redirect('product_list')

    product = get_object_or_404(Product, id=product_id, available=True)

    try:
        session = stripe.checkout.Session.create(
            customer_creation='always',
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': product.price,       # from the database
                    'product_data': {
                        'name': product.name,           # from the database
                        'description': product.description,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            # Store product_id in metadata so success view can look it up
            metadata={'product_id': product.id},
            success_url=(
                request.build_absolute_uri('/success/')
                + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        return render(request, 'store/error.html', {'error': str(e)})


# ------------------------------------------------------------------
# 3. Success — retrieve session, save Order to database, show confirmation
# ------------------------------------------------------------------
def payment_success(request):
    session_id = request.GET.get('session_id')
    order = None

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            # Guard: avoid duplicate rows if user refreshes the success page
            if not Order.objects.filter(stripe_session_id=session_id).exists():
                product_id = session.metadata['product_id']
                product    = get_object_or_404(Product, id=product_id)

                order = Order.objects.create(
                    product           = product,
                    stripe_session_id = session_id,
                    customer_email    = session.customer_details.email,
                    amount_paid       = session.amount_total,
                    currency          = session.currency.upper(),
                    status            = 'complete',
                )
            else:
                order = Order.objects.get(stripe_session_id=session_id)

       
        
        except (stripe.error.StripeError, Exception):
            pass

    return render(request, 'store/success.html', {'order': order})


# ------------------------------------------------------------------
# 4. Cancel — Stripe redirects here if the user abandons checkout
# ------------------------------------------------------------------
def payment_cancel(request):
    return render(request, 'store/cancel.html')