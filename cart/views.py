from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

from .models import Cart, CartItem, WishlistItem
from products.models import Product
from .forms import AddToCartForm
from .utils import get_or_create_cart


def cart_detail(request):
    """Display cart contents."""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product__brand').prefetch_related('product__images'),
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def add_to_cart(request):
    """Add product to cart via AJAX or form submission."""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # For AJAX requests, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'redirect_url': reverse('accounts:login')
            })
        # For regular form submissions, redirect to login
        return redirect('accounts:login')
    
    form = AddToCartForm(request.POST)
    
    if form.is_valid():
        product_id = form.cleaned_data['product_id']
        quantity = form.cleaned_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Product not found'})
            messages.error(request, 'Product not found.')
            return redirect('cart:cart_detail')
        
        # Check stock availability
        if product.manage_stock and product.stock_quantity < quantity:
            error_msg = f'Only {product.stock_quantity} items available in stock.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('products:product_detail', slug=product.slug)
        
        # Add to cart
        cart = get_or_create_cart(request)
        cart_item = cart.add_item(product, quantity)
        
        success_msg = f'{product.name} added to cart successfully!'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'cart_total_items': cart.total_items,
                'cart_total_price': str(cart.total_price),
            })
        
        messages.success(request, success_msg)
        return redirect('cart:cart_detail')
    
    # Form validation failed
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid form data'})
    
    messages.error(request, 'Invalid form data.')
    return redirect('cart:cart_detail')


@require_POST
def update_cart_item(request):
    """Update cart item quantity via AJAX."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required',
            'redirect_url': reverse('accounts:login')
        })
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 0))
        
        if quantity < 0:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
        
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if quantity == 0:
            cart.remove_item(product)
            message = f'{product.name} removed from cart.'
        else:
            # Check stock availability
            if product.manage_stock and product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {product.stock_quantity} items available in stock.'
                })
            
            cart.update_item_quantity(product, quantity)
            message = 'Cart updated successfully.'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_total_price': str(cart.total_price),
        })
        
    except (json.JSONDecodeError, ValueError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid request data'})


@require_POST
def remove_from_cart(request, product_id):
    """Remove item from cart."""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'redirect_url': reverse('accounts:login')
            })
        return redirect('accounts:login')
    
    cart = get_or_create_cart(request)
    
    try:
        product = Product.objects.get(id=product_id)
        if cart.remove_item(product):
            success_msg = f'{product.name} removed from cart.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'cart_total_items': cart.total_items,
                    'cart_total_price': str(cart.total_price),
                })
            messages.success(request, success_msg)
        else:
            error_msg = 'Item not found in cart.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            
    except Product.DoesNotExist:
        error_msg = 'Product not found.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
    
    return redirect('cart:cart_detail')


def clear_cart(request):
    """Clear all items from cart."""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'redirect_url': reverse('accounts:login')
            })
        return redirect('accounts:login')
    
    cart = get_or_create_cart(request)
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully.',
            'cart_total_items': 0,
            'cart_total_price': '0.00',
        })
    
    messages.success(request, 'Cart cleared successfully.')
    return redirect('cart:cart_detail')


@login_required
def wishlist_view(request):
    """Display user's wishlist."""
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related(
        'product__brand'
    ).prefetch_related('product__images')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'cart/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            message = f'{product.name} added to wishlist.'
            success = True
        else:
            message = f'{product.name} is already in your wishlist.'
            success = False
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': success, 'message': message})
        
        if success:
            messages.success(request, message)
        else:
            messages.info(request, message)
            
    except Product.DoesNotExist:
        message = 'Product not found.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': message})
        messages.error(request, message)
    
    return redirect('products:product_detail', slug=product.slug)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    try:
        wishlist_item = WishlistItem.objects.get(user=request.user, product_id=product_id)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        
        message = f'{product_name} removed from wishlist.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': message})
        
        messages.success(request, message)
        
    except WishlistItem.DoesNotExist:
        message = 'Item not found in wishlist.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': message})
        messages.error(request, message)
    
    return redirect('cart:wishlist')