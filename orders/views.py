import secrets
import string
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json

from cart.cart import Cart
from users.models import Address
from .models import Order, OrderItem, ShippingMethod
from .forms import OrderCreateForm

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


def generate_order_number():
    """Generate a unique order number"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_number = generate_order_number()
            
            if request.user.is_authenticated:
                order.user = request.user
            
            # Calculate totals
            order.subtotal = cart.get_total_price()
            
            # Calculate shipping (basic implementation)
            total_weight = sum(
                Decimal(str(item['product'].weight)) * item['quantity'] 
                for item in cart
            )
            shipping_method = ShippingMethod.objects.filter(is_active=True).first()
            if shipping_method:
                order.shipping_cost = shipping_method.calculate_cost(total_weight)
            
            # Calculate tax (basic 8% implementation)
            order.tax_amount = order.subtotal * Decimal('0.08')
            order.total_amount = order.subtotal + order.shipping_cost + order.tax_amount
            
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Store order in session for payment
            request.session['order_id'] = order.id
            
            return redirect('orders:payment', order_id=order.id)
    else:
        form = OrderCreateForm()
        
        # Pre-fill form for authenticated users
        if request.user.is_authenticated:
            form.fields['email'].initial = request.user.email
            form.fields['first_name'].initial = request.user.first_name
            form.fields['last_name'].initial = request.user.last_name
            
            # Get default addresses
            billing_address = request.user.addresses.filter(
                type='billing', is_default=True
            ).first()
            shipping_address = request.user.addresses.filter(
                type='shipping', is_default=True
            ).first()
            
            if billing_address:
                form.set_address_data('billing_', billing_address)
            if shipping_address:
                form.set_address_data('shipping_', shipping_address)
    
    return render(request, 'orders/create.html', {
        'form': form,
        'cart': cart
    })


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Verify order belongs to session or user
    if (request.session.get('order_id') != order.id and 
        (not request.user.is_authenticated or order.user != request.user)):
        messages.error(request, 'Invalid order access')
        return redirect('products:product_list')
    
    # Create Stripe PaymentIntent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number,
            }
        )
        
        return render(request, 'orders/payment.html', {
            'order': order,
            'client_secret': intent.client_secret,
            'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('orders:order_create')


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        payment_intent_id = payload.get('payment_intent_id')
        
        try:
            # Retrieve the PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                order_id = intent.metadata.get('order_id')
                order = get_object_or_404(Order, id=order_id)
                
                # Update order status
                order.payment_status = 'completed'
                order.payment_method = 'stripe'
                order.payment_reference = payment_intent_id
                order.status = 'processing'
                order.save()
                
                # Clear cart
                cart = Cart(request)
                cart.clear()
                
                # Send confirmation email
                send_order_confirmation_email(order)
                
                return JsonResponse({'success': True, 'order_id': order.id})
            
        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Verify access
    if (not request.user.is_authenticated or 
        (order.user and order.user != request.user)):
        messages.error(request, 'Invalid order access')
        return redirect('products:product_list')
    
    return render(request, 'orders/success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - {order.order_number}'
    html_message = render_to_string('orders/email/confirmation.html', {'order': order})
    
    try:
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")