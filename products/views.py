from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.http import JsonResponse

from .models import Product, Category, Brand, ProductReview
from cart.forms import AddToCartForm


class ProductListView(ListView):
    """Product listing with filtering and search."""
    
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Brand filter
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Condition filter
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # In stock filter
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['name', '-name', 'price', '-price', '-created_at', 'created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent=None)
        context['brands'] = Brand.objects.filter(is_active=True)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'brand': self.request.GET.get('brand', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'condition': self.request.GET.get('condition', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        return context


class ProductDetailView(DetailView):
    """Product detail page with reviews and related products."""
    
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related(
            'images', 'attributes__attribute', 'reviews__user'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Add to cart form
        context['add_to_cart_form'] = AddToCartForm()
        
        # Product reviews
        reviews = ProductReview.objects.filter(product=product, is_approved=True).select_related('user')
        context['reviews'] = reviews[:10]  # Show first 10 reviews
        context['total_reviews'] = reviews.count()
        
        # Rating distribution
        rating_counts = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')
        context['rating_distribution'] = {item['rating']: item['count'] for item in rating_counts}
        
        # Related products
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).select_related('brand').prefetch_related('images')[:4]
        context['related_products'] = related_products
        
        return context


class CategoryDetailView(DetailView):
    """Category page with products."""
    
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get products in this category
        products = Product.objects.filter(
            category=category, 
            is_active=True
        ).select_related('brand').prefetch_related('images')
        
        # Apply filters similar to ProductListView
        search_query = self.request.GET.get('search')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        
        # Subcategories
        context['subcategories'] = category.subcategories.filter(is_active=True)
        
        return context


def search_suggestions(request):
    """AJAX endpoint for search suggestions."""
    query = request.GET.get('q', '')
    suggestions = []
    
    if len(query) >= 2:
        # Product suggestions
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query),
            is_active=True
        ).select_related('brand')[:5]
        
        for product in products:
            suggestions.append({
                'type': 'product',
                'name': product.name,
                'brand': product.brand.name,
                'url': product.get_absolute_url(),
                'price': str(product.get_price),
            })
        
        # Category suggestions
        categories = Category.objects.filter(
            name__icontains=query, 
            is_active=True
        )[:3]
        
        for category in categories:
            suggestions.append({
                'type': 'category',
                'name': category.name,
                'url': category.get_absolute_url(),
            })
    
    return JsonResponse({'suggestions': suggestions})