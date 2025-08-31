from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json

from products.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    if quantity <= 0:
        quantity = 1
    
    # Check stock availability
    if quantity > product.stock_quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Only {product.stock_quantity} items available in stock'
            })
        messages.error(request, f'Only {product.stock_quantity} items available in stock')
        return redirect('products:product_detail', slug=product.slug)
    
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price()),
            'message': f'{product.name} added to cart'
        })
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('cart:cart_detail')


@csrf_exempt
def cart_remove(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total_items': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'message': f'{product.name} removed from cart'
            })
        
        messages.success(request, f'{product.name} removed from cart')
    
    return redirect('cart:cart_detail')


@csrf_exempt 
def cart_update(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError, TypeError):
            quantity = 1
        
        if quantity <= 0:
            cart.remove(product)
            message = f'{product.name} removed from cart'
        else:
            if quantity > product.stock_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock_quantity} items available'
                })
            
            cart.add(product=product, quantity=quantity, override_quantity=True)
            message = f'{product.name} quantity updated'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total_items': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'item_total': str(product.price * quantity) if quantity > 0 else '0',
                'message': message
            })
    
    return redirect('cart:cart_detail')