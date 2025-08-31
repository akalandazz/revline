from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from products.models import Product, Category, Brand
from .models import Banner, Newsletter, ContactMessage, SiteSettings
from .forms import NewsletterForm, ContactForm


def home(request):
    """Homepage view with featured products and banners."""
    context = {
        # Hero banners
        'hero_banners': Banner.objects.filter(banner_type='hero', is_active=True)[:3],
        
        # Featured products
        'featured_products': Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('brand').prefetch_related('images')[:8],
        
        # New arrivals
        'new_products': Product.objects.filter(
            is_active=True
        ).select_related('brand').prefetch_related('images').order_by('-created_at')[:8],
        
        # Categories
        'categories': Category.objects.filter(is_active=True, parent=None)[:6],
        
        # Brands
        'brands': Brand.objects.filter(is_active=True)[:8],
        
        # Newsletter form
        'newsletter_form': NewsletterForm(),
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About us page."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page with form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'core/contact.html', context)


@require_POST
def newsletter_subscribe(request):
    """Newsletter subscription via AJAX."""
    form = NewsletterForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        newsletter, created = Newsletter.objects.get_or_create(email=email)
        
        if created:
            message = 'Thank you for subscribing to our newsletter!'
            success = True
        else:
            if newsletter.is_active:
                message = 'You are already subscribed to our newsletter.'
                success = False
            else:
                newsletter.is_active = True
                newsletter.save()
                message = 'Welcome back! Your subscription has been reactivated.'
                success = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': success, 'message': message})
        
        if success:
            messages.success(request, message)
        else:
            messages.info(request, message)
    else:
        error_message = 'Please enter a valid email address.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_message})
        messages.error(request, error_message)
    
    return redirect('core:home')


def search(request):
    """Global search functionality."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('products:product_list')
    
    # Search products
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(brand__name__icontains=query) |
        Q(category__name__icontains=query) |
        Q(compatible_makes__icontains=query) |
        Q(compatible_models__icontains=query),
        is_active=True
    ).select_related('brand', 'category').prefetch_related('images').distinct()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'products': products_page,
        'total_results': paginator.count,
    }
    return render(request, 'core/search_results.html', context)


def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    """Terms of service page."""
    return render(request, 'core/terms_of_service.html')


def shipping_returns(request):
    """Shipping and returns information page."""
    context = {
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'core/shipping_returns.html', context)


def faq(request):
    """Frequently asked questions page."""
    return render(request, 'core/faq.html')