from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import json

from cart.utils import get_or_create_cart
from .models import Order, OrderItem, ShippingMethod, OrderStatusHistory
from .forms import (
    CheckoutContactForm, ShippingAddressForm, BillingAddressForm,
    ShippingMethodForm, PaymentForm, OrderReviewForm
)


def checkout_start(request):
    """Start the checkout process."""
    cart = get_or_create_cart(request)
    
    # Check if cart is empty
    if cart.is_empty:
        messages.warning(request, 'Your cart is empty. Please add some items before checkout.')
        return redirect('cart:cart_detail')
    
    # Check stock availability for all items
    for item in cart.items.all():
        if item.product.manage_stock and item.product.stock_quantity < item.quantity:
            messages.error(
                request, 
                f'Sorry, only {item.product.stock_quantity} units of {item.product.name} are available.'
            )
            return redirect('cart:cart_detail')
    
    # Store cart in session for checkout process
    request.session['checkout_cart_id'] = cart.id
    
    return redirect('checkout:contact')


def checkout_contact(request):
    """Step 1: Contact information."""
    cart = get_checkout_cart(request)
    if not cart:
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = CheckoutContactForm(request.POST, user=request.user)
        if form.is_valid():
            # Store contact info in session
            request.session['checkout_contact'] = form.cleaned_data
            return redirect('checkout:shipping')
    else:
        # Pre-fill form with session data if available
        initial_data = request.session.get('checkout_contact', {})
        form = CheckoutContactForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'cart': cart,
        'step': 1,
        'step_name': 'Contact Information'
    }
    return render(request, 'checkout/contact.html', context)


def checkout_shipping(request):
    """Step 2: Shipping address."""
    cart = get_checkout_cart(request)
    if not cart or 'checkout_contact' not in request.session:
        return redirect('checkout:contact')
    
    if request.method == 'POST':
        # Check if user selected a saved address
        saved_address_id = request.POST.get('saved_address')
        
        if saved_address_id and saved_address_id != 'new' and request.user.is_authenticated:
            # User selected a saved address
            try:
                from accounts.models import Address
                address = Address.objects.get(
                    id=saved_address_id,
                    user=request.user,
                    address_type='shipping'
                )
                
                # Store shipping info from saved address in session
                shipping_data = {
                    'street_address': address.street_address,
                    'apartment': address.apartment,
                    'city': address.city,
                    'state': address.state,
                    'postal_code': address.postal_code,
                    'country': address.country,
                }
                request.session['checkout_shipping'] = shipping_data
                
                # Handle save address checkbox if present
                if request.POST.get('save_address'):
                    # Address is already saved, no need to save again
                    pass
                
                return redirect('checkout:billing')
                
            except Address.DoesNotExist:
                messages.error(request, 'Selected address not found.')
        else:
            # User entered new address
            form = ShippingAddressForm(request.POST, user=request.user)
            if form.is_valid():
                # Store shipping info in session
                shipping_data = form.cleaned_data
                request.session['checkout_shipping'] = shipping_data
                
                # Save address if requested and user is authenticated
                if request.POST.get('save_address') and request.user.is_authenticated:
                    try:
                        from accounts.models import Address
                        Address.objects.create(
                            user=request.user,
                            address_type='shipping',
                            street_address=shipping_data['street_address'],
                            apartment=shipping_data.get('apartment', ''),
                            city=shipping_data['city'],
                            state=shipping_data['state'],
                            postal_code=shipping_data['postal_code'],
                            country=shipping_data['country'],
                            is_default=False  # Don't make it default automatically
                        )
                        messages.success(request, 'Address saved for future use.')
                    except Exception as e:
                        # Don't fail checkout if address saving fails
                        messages.warning(request, 'Address could not be saved, but checkout will continue.')
                
                return redirect('checkout:billing')
    else:
        # Pre-fill form with session data if available
        initial_data = request.session.get('checkout_shipping', {})
        form = ShippingAddressForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'cart': cart,
        'step': 2,
        'step_name': 'Shipping Address'
    }
    return render(request, 'checkout/shipping.html', context)


def checkout_billing(request):
    """Step 3: Billing address."""
    cart = get_checkout_cart(request)
    if not cart or 'checkout_shipping' not in request.session:
        return redirect('checkout:shipping')
    
    if request.method == 'POST':
        form = BillingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            # Store billing info in session
            request.session['checkout_billing'] = form.cleaned_data
            return redirect('checkout:shipping_method')
    else:
        # Pre-fill form with session data if available
        initial_data = request.session.get('checkout_billing', {})
        form = BillingAddressForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'cart': cart,
        'step': 3,
        'step_name': 'Billing Address'
    }
    return render(request, 'checkout/billing.html', context)


def checkout_shipping_method(request):
    """Step 4: Shipping method selection."""
    cart = get_checkout_cart(request)
    if not cart or 'checkout_billing' not in request.session:
        return redirect('checkout:billing')
    
    if request.method == 'POST':
        form = ShippingMethodForm(request.POST, order_total=cart.total_price)
        if form.is_valid():
            # Store shipping method in session
            shipping_method = form.cleaned_data['shipping_method']
            request.session['checkout_shipping_method'] = {
                'id': shipping_method.id,
                'name': shipping_method.name,
                'cost': str(shipping_method.cost),
                'estimated_days': shipping_method.estimated_days
            }
            return redirect('checkout:payment')
    else:
        # Pre-fill form with session data if available
        initial_data = {}
        if 'checkout_shipping_method' in request.session:
            try:
                method_id = request.session['checkout_shipping_method']['id']
                initial_data['shipping_method'] = ShippingMethod.objects.get(id=method_id)
            except (ShippingMethod.DoesNotExist, KeyError):
                pass
        
        form = ShippingMethodForm(initial=initial_data, order_total=cart.total_price)
    
    context = {
        'form': form,
        'cart': cart,
        'step': 4,
        'step_name': 'Shipping Method'
    }
    return render(request, 'checkout/shipping_method.html', context)


def checkout_payment(request):
    """Step 5: Payment information."""
    cart = get_checkout_cart(request)
    if not cart or 'checkout_shipping_method' not in request.session:
        return redirect('checkout:shipping_method')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Store payment info in session (excluding sensitive data)
            payment_data = form.cleaned_data.copy()
            # Remove sensitive credit card data from session
            if 'card_number' in payment_data:
                del payment_data['card_number']
            if 'card_cvv' in payment_data:
                del payment_data['card_cvv']
            
            request.session['checkout_payment'] = payment_data
            return redirect('checkout:review')
    else:
        # Pre-fill form with session data if available
        initial_data = request.session.get('checkout_payment', {})
        form = PaymentForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'step': 5,
        'step_name': 'Payment Information'
    }
    return render(request, 'checkout/payment.html', context)


def checkout_review(request):
    """Step 6: Order review and confirmation."""
    cart = get_checkout_cart(request)
    if not cart or 'checkout_payment' not in request.session:
        return redirect('checkout:payment')
    
    # Calculate order totals
    subtotal = cart.total_price
    shipping_method_data = request.session.get('checkout_shipping_method', {})
    shipping_cost = Decimal(shipping_method_data.get('cost', '0.00'))
    tax_amount = Decimal('0.00')  # You can implement tax calculation here
    total_amount = subtotal + shipping_cost + tax_amount
    
    if request.method == 'POST':
        form = OrderReviewForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the order
                    order = create_order_from_session(request, cart, total_amount, shipping_cost, tax_amount)
                    
                    # Clear cart and session data
                    cart.clear()
                    clear_checkout_session(request)
                    
                    # Send confirmation email
                    send_order_confirmation_email(order)
                    
                    messages.success(request, f'Your order #{order.order_number} has been placed successfully!')
                    return redirect('checkout:success', order_number=order.order_number)
                    
            except Exception as e:
                messages.error(request, 'There was an error processing your order. Please try again.')
                return redirect('checkout:review')
    else:
        form = OrderReviewForm()
    
    # Get all checkout data for review
    contact_data = request.session.get('checkout_contact', {})
    shipping_data = request.session.get('checkout_shipping', {})
    billing_data = request.session.get('checkout_billing', {})
    payment_data = request.session.get('checkout_payment', {})
    
    context = {
        'form': form,
        'cart': cart,
        'contact_data': contact_data,
        'shipping_data': shipping_data,
        'billing_data': billing_data,
        'payment_data': payment_data,
        'shipping_method_data': shipping_method_data,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'step': 6,
        'step_name': 'Review Order'
    }
    return render(request, 'checkout/review.html', context)


def checkout_success(request, order_number):
    """Order success page."""
    try:
        if request.user.is_authenticated:
            order = Order.objects.get(order_number=order_number, user=request.user)
        else:
            # For guest orders, check session or email
            order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')
    
    context = {
        'order': order,
    }
    return render(request, 'checkout/success.html', context)


@login_required
def order_detail(request, order_number):
    """View order details."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'checkout/order_detail.html', context)


@login_required
def order_list(request):
    """List user's orders."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    context = {
        'orders': orders,
    }
    return render(request, 'checkout/order_list.html', context)


# Helper functions

def get_checkout_cart(request):
    """Get cart for checkout process."""
    cart_id = request.session.get('checkout_cart_id')
    if cart_id:
        try:
            from cart.models import Cart
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            pass
    return None


def create_order_from_session(request, cart, total_amount, shipping_cost, tax_amount):
    """Create order from session data."""
    contact_data = request.session.get('checkout_contact', {})
    shipping_data = request.session.get('checkout_shipping', {})
    billing_data = request.session.get('checkout_billing', {})
    payment_data = request.session.get('checkout_payment', {})
    shipping_method_data = request.session.get('checkout_shipping_method', {})
    
    # Handle billing address same as shipping
    if billing_data.get('same_as_shipping', True):
        billing_address = shipping_data.copy()
    else:
        billing_address = {
            'street_address': billing_data.get('street_address', ''),
            'apartment': billing_data.get('apartment', ''),
            'city': billing_data.get('city', ''),
            'state': billing_data.get('state', ''),
            'postal_code': billing_data.get('postal_code', ''),
            'country': billing_data.get('country', 'United States'),
        }
    
    # Create order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=contact_data.get('email', ''),
        first_name=contact_data.get('first_name', ''),
        last_name=contact_data.get('last_name', ''),
        phone_number=contact_data.get('phone_number', ''),
        
        # Shipping address
        shipping_street_address=shipping_data.get('street_address', ''),
        shipping_apartment=shipping_data.get('apartment', ''),
        shipping_city=shipping_data.get('city', ''),
        shipping_state=shipping_data.get('state', ''),
        shipping_postal_code=shipping_data.get('postal_code', ''),
        shipping_country=shipping_data.get('country', 'United States'),
        
        # Billing address
        billing_street_address=billing_address.get('street_address', ''),
        billing_apartment=billing_address.get('apartment', ''),
        billing_city=billing_address.get('city', ''),
        billing_state=billing_address.get('state', ''),
        billing_postal_code=billing_address.get('postal_code', ''),
        billing_country=billing_address.get('country', 'United States'),
        
        # Order totals
        subtotal=cart.total_price,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        total_amount=total_amount,
        
        # Payment info
        payment_method=payment_data.get('payment_method', ''),
        notes=payment_data.get('notes', ''),
    )
    
    # Create order items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
        )
        
        # Update product stock if managed
        if cart_item.product.manage_stock:
            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save()
    
    # Create initial status history
    OrderStatusHistory.objects.create(
        order=order,
        status='pending',
        notes='Order placed',
        created_by=request.user if request.user.is_authenticated else None
    )
    
    return order


def clear_checkout_session(request):
    """Clear checkout session data."""
    session_keys = [
        'checkout_cart_id',
        'checkout_contact',
        'checkout_shipping',
        'checkout_billing',
        'checkout_shipping_method',
        'checkout_payment'
    ]
    
    for key in session_keys:
        if key in request.session:
            del request.session[key]


def send_order_confirmation_email(order):
    """Send order confirmation email."""
    try:
        subject = f'Order Confirmation #{order.order_number}'
        html_message = render_to_string('checkout/emails/order_confirmation.html', {'order': order})
        plain_message = render_to_string('checkout/emails/order_confirmation.txt', {'order': order})
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        # Log error but don't fail the order
        print(f"Failed to send confirmation email: {e}")